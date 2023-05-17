from aws_cdk import (
    aws_ssm as ssm,
    aws_iam as iam,
    core
)
import yaml
import os

class FisSsmDocs(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Deploy the SSMA document to inject the Nacl faults
        file = os.path.join(os.path.dirname(__file__), "documents/ssma-nacl-faults.yml")
        with open(file, "r") as nacl_file:
            nacl_content = nacl_file.read()
            nacl_cfnDocument = ssm.CfnDocument(
                self, "Nacl-SSM-Document",
                content=yaml.safe_load(nacl_content),
                document_type="Automation",
                document_format="YAML"
            )

        # Deploy the SSMA document to inject the security group faults
        file = os.path.join(os.path.dirname(__file__), "documents/security-groups-faults.yml")
        with open(file, "r") as secgroup_file:
            secgroup_content = secgroup_file.read()
            secgroup_cfnDocument = ssm.CfnDocument(
                self, "SecGroup-SSM-Document",
                content=yaml.safe_load(secgroup_content),
                document_type="Automation",
                document_format="YAML"
            )

        # Deploy the SSMA document to inject the Iam Access faults
        file = os.path.join(os.path.dirname(__file__), "documents/iam-access-faults.yml")
        with open(file, "r") as iamaccess_file:
            iamaccess_content = iamaccess_file.read()

import yaml
import os
import boto3
from aws_cdk import (
    aws_iam as iam,
    aws_ssm as ssm,
    core,
)

iamaccess_content = open(os.path.join(os.path.dirname(__file__), "documents/iamaccess.yml")).read()
iamaccess_cfnDocument = ssm.CfnDocument(
    scope = self,
    id = "IamAccess-SSM-Document",
    content = yaml.load(iamaccess_content),
    document_type = "Automation",
    document_format = "YAML",
)

parameterstore_content = open(os.path.join(os.path.dirname(__file__), "documents/ssma-put-config-parameterstore.yml")).read()
parameterstore_cfnDocument = ssm.CfnDocument(
    scope = self,
    id = "ParameterStore-SSM-Document",
    content = yaml.load(parameterstore_content),
    document_type = "Automation",
    document_format = "YAML",
)

iamAccessFaultRole = self.node.try_get_context("target_role_name")
ssmaNaclRole = iam.Role(
    scope = self,
    id = "ssma-nacl-role",
    assumed_by = iam.CompositePrincipal(
        iam.ServicePrincipal("iam.amazonaws.com"),
        iam.ServicePrincipal("ssm.amazonaws.com")
    ),
)
ssmaroleAsCfn = ssmaNaclRole.node.default_child
ssmaroleAsCfn.add_override(
    "Properties.AssumeRolePolicyDocument.Statement.0.Principal.Service",
    ["ssm.amazonaws.com", "iam.amazonaws.com"]
)
ssmaNaclRole.add_to_policy(
    iam.PolicyStatement(
        resources = ["*"],
        actions = [
            "ec2:DescribeInstances",
          "ec2:CreateNetworkAcl",
          "ec2:CreateTags",
          "ec2:CreateNetworkAclEntry",
          "ec2:DescribeSubnets",
          "ec2:DescribeNetworkAcls",
          "ec2:ReplaceNetworkAclAssociation",
          "ec2:DeleteNetworkAcl",
        ],
    )
)

ssmaNaclRole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["iam:ListRoles"],
        resources=["*"]
    )
)

ssmaNaclRole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "logs:CreateLogStream",
            "logs:CreateLogGroup",
            "logs:PutLogEvents",
            "logs:DescribeLogGroups",
            "logs:DescribeLogStreams",
        ],
        resources=["*"]
    )
)

ssmaSecGroupRole = iam.Role(
    scope=self,
    id="ssma-secgroup-role",
    assumed_by=iam.CompositePrincipal(
        iam.ServicePrincipal("iam.amazonaws.com"),
        iam.ServicePrincipal("ssm.amazonaws.com")
    )
)

ssmaSecGroupRole_as_cfn = ssmaSecGroupRole.node.default_child
ssmaSecGroupRole_as_cfn.add_override(
    "Properties.AssumeRolePolicyDocument.Statement.0.Principal.Service",
    ["ssm.amazonaws.com", "iam.amazonaws.com"]
)

ssmaSecGroupRole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "ec2:RevokeSecurityGroupIngress",
            "ec2:AuthorizeSecurityGroupIngress",
            "ec2:DescribeSecurityGroups",
        ],
        resources=["*"]
    )
)

# Additional Permissions for logging
ssma_sec_group_role.add_to_policy(
    iam.PolicyStatement(
        resources=["*"],
        actions=[
            "logs:CreateLogStream",
            "logs:CreateLogGroup",
            "logs:PutLogEvents",
            "logs:DescribeLogGroups",
            "logs:DescribeLogStreams",
        ],
    )
)

# IAM role access faults 'ssma-iam-access-faults.yml'
ssma_iam_access_role = iam.Role(
    self,
    "ssma-iam-access-role",
    assumed_by=iam.CompositePrincipal(
        iam.ServicePrincipal("iam.amazonaws.com"),
        iam.ServicePrincipal("ssm.amazonaws.com"),
    ),
)
ssma_iam_access_role_as_cfn = ssma_iam_access_role.node.default_child
ssma_iam_access_role_as_cfn.add_override(
    "Properties.AssumeRolePolicyDocument.Statement.0.Principal.Service",
    ["ssm.amazonaws.com", "iam.amazonaws.com"],
)

# GetRoleandPolicyDetails
ssma_iam_access_role.add_to_policy(
    iam.PolicyStatement(
        resources=[
            f"arn:aws:iam::{self.account}:role/{iam_access_fault_role}",
            f"arn:aws:iam::{self.account}:policy/*",
        ],
        actions=[
            "iam:GetRole",
            "iam:GetPolicy",
            "iam:ListAttachedRolePolicies",
            "iam:ListRoles",
        ],
    )
)

# IAM role access faults 'ssma-put-config-parameterstore.yml'
ssmParameterName = self.node.try_get_context("ssm_parameter_name")
ssmaPutParameterStoreRole = iam.Role(
    self,
    "ssma-put-parameterstore-role",
    assumed_by=iam.CompositePrincipal(
        iam.ServicePrincipal("iam.amazonaws.com"),
        iam.ServicePrincipal("ssm.amazonaws.com")
    )
)
ssmaPutParameterStoreRoleAsCfn = ssmaPutParameterStoreRole.node.default_child
ssmaPutParameterStoreRoleAsCfn.add_override(
    "Properties.AssumeRolePolicyDocument.Statement.0.Principal.Service",
    ["ssm.amazonaws.com", "iam.amazonaws.com"]
)
# GetRoleandPolicyDetails
ssmaPutParameterStoreRole.add_to_policy(
    iam.PolicyStatement(
        resources=[
            f"arn:aws:ssm:{self.region}:{self.account}:parameter/{ssmParameterName}"
        ],
        actions=["ssm:PutParameter"]
    )
)
# Additional Permissions for logging
ssmaPutParameterStoreRole.add_to_policy(
    iam.PolicyStatement(
        resources=["*"],
        actions=[
            "logs:CreateLogStream",
            "logs:CreateLogGroup",
            "logs:PutLogEvents",
            "logs:DescribeLogGroups",
            "logs:DescribeLogStreams"
        ]
    )
)

# Outputs
CfnOutput(self, "NaclSSMADocName", 
          value=nacl_cfnDocument.ref!, 
          description="The name of the SSM Doc", 
          export_name="NaclSSMADocName")
CfnOutput(self, "SecGroupSSMADocName", 
          value=secgroup_cfnDocument.ref!, 
          description="The name of the SSM Doc", 
          export_name="SecGroupSSMADocName")
CfnOutput(self, "IamAccessSSMADocName", 
          value=iamaccess_cfnDocument.ref!, 
          description="The name of the SSM Doc", 
          export_name="IamAccessSSMADocName")
CfnOutput(self, "PutParameterStoreSSMADocName", 
          value=parameterstore_cfnDocument.ref!, 
          description="The name of the SSM Doc", 
          export_name="PutParameterStoreSSMADocName")
CfnOutput(self, "SSMANaclRoleArn", 
          value=ssmaNaclRole.roleArn, 
          description="The Arn of the IAM role", 
          export_name="SSMANaclRoleArn")
CfnOutput(self, "SSMASecGroupRoleArn", 
          value=ssmaSecGroupRole.roleArn, 
          description="The Arn of the IAM role", 
          export_name="SSMASecGroupRoleArn")
CfnOutput(self, "SSMAIamAccessRoleArn", 
          value=ssmaIamAccessRole.roleArn, 
          description="The Arn of the IAM role", 
          export_name="SSMAIamAccessRoleArn")
CfnOutput(self, "SSMAPutParameterStoreRoleArn", 
          value=ssmaPutParameterStoreRole.roleArn, 
          description="The Arn of the IAM role", 
          export_name="SSMAPutParameterStoreRoleArn")

