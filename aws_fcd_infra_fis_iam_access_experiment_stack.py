import boto3
from aws_cdk import (
    aws_iam as iam,
    aws_fis as fis,
    core as cdk
)

class IamAccessExperiments(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Import FIS Role, Stop Condition, and other required parameters
        importedFISRoleArn = cdk.Fn.import_value("FISIamRoleArn")
        importedStopConditionArn = cdk.Fn.import_value("StopConditionArn")
        importedSSMAIamAccessRoleArn = cdk.Fn.import_value("SSMAIamAccessRoleArn")
        importedIamAccessSSMADocName = cdk.Fn.import_value("IamAccessSSMADocName")
        importedTargetRoleName = self.node.try_get_context("target_role_name")
        importedS3BucketToDeny = self.node.try_get_context("s3-bucket-to-deny")

        # Create S3 Fault Policy
        s3_fault_policy = iam.ManagedPolicy(
            self,
            "s3-deny",
            statements=[
                iam.PolicyStatement(
                    sid="DenyAccessToS3Resources",
                    resources=[f"arn:aws:s3:::{importedS3BucketToDeny}"],
                    actions=["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                    effect=iam.Effect.DENY,
                )
            ]
        )

        # Actions
start_automation = {
    "actionId": "aws:ssm:start-automation-execution",
    "description": "Deny Access to a S3 Resoure Type for a Role.",
    "parameters": {
        "documentArn": f"arn:aws:ssm:{self.region}:{self.account}:document/{importedIamAccessSSMADocName}",
        "documentParameters": json.dumps({
            "DurationMinutes": "PT1M",
            "AutomationAssumeRole": importedSSMAIamAccessRoleArn,
            "AccessDenyPolicyArn": f"arn:aws:iam::{self.account}:policy/{s3FaultPolicy.managedPolicyName}",
            "TargetRoleName": importedTargetRoleName,
        }),
        "maxDuration": "PT5M",
    },
}

# Experiments
template_inject_s3_access_denied = fis.CfnExperimentTemplate(
    self,
    "fis-template-inject-s3-access-denied",
    description="Deny Access to an S3 bucket via an IAM role",
    role_arn=importedFISRoleArn,
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": importedStopConditionArn,
        },
    ],
    tags={
        "Name": "Deny Access to an S3 bucket",
        "Stackname": self.stack_name,
    },
    actions={
        "ssmaAction": start_automation,
    },
    targets={},
)


