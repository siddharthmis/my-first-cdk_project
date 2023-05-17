import boto3
import cdk from "aws-cdk-lib"
from constructs import Construct
from aws_cdk_lib.aws_fis as fis
from aws_cdk_lib.aws_ec2 as ec2

class Ec2ControlPlaneExperiments(Stack):
    def __init__(self, scope: Construct, id: str, props: StackProps = None):
        super().__init__(scope, id, props)
        # Import FIS Role and Stop Condition
        imported_fis_role_arn = cdk.Fn.import_value("FISIamRoleArn")
        imported_stop_condition_arn = cdk.Fn.import_value("StopConditionArn")
        target_role_name = self.node.try_get_context("target_role_name")
        # Targets
        target_iam_role = {
            "resourceType": "aws:iam:role",
            "selectionMode": "ALL",
            "resourceArns": [
                f"arn:aws:iam::{self.account}:role/{target_role_name}"
            ]
        }
        # Actions
        internal_error = {
            "actionId": "aws:fis:inject-api-internal-error",
            "description": "Defining the API operations and percentage of requets to fail",
            "parameters": {
                "service": "ec2",
                "operations": "DescribeInstances,DescribeVolumes",
                "percentage": "100",
                "duration": "PT2M"
            },
            "targets": {
                "Roles": "roleTargets"
            }
        }
        throttleError = {
    "actionId": "aws:fis:inject-api-throttle-error",
    "description": "Defining the API operations",
    "parameters": {
        "service": "ec2",
        "operations": "DescribeInstances,DescribeVolumes",
        "percentage": "100",
        "duration": "PT2M"
    },
    "targets": {
        "Roles": "roleTargets"
    }
}
unavailableError = {
    "actionId": "aws:fis:inject-api-unavailable-error",
    "description": "Defining the API operations and percentage of requets to throttle",
    "parameters": {
        "service": "ec2",
        "operations": "DescribeInstances,DescribeVolumes",
        "percentage": "100",
        "duration": "PT2M"
    },
    "targets": {
        "Roles": "roleTargets"
    }
}
templateInternalError = fis.CfnExperimentTemplate(
    self,
    "fis-template-inject-internal-error",
    description="Inject EC2 API Internal Error",
    role_arn=importedFISRoleArn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": importedStopConditionArn.to_string()
        }
    ],
    tags={
        "Name": "EC2 API Internal Error",
        "Stackname": self.stack_name
    },
    actions={
        "instanceActions": internalError
    },
    targets={
        "roleTargets": TargetIAMRole
    }
)
templateUnavailableError = fis.CfnExperimentTemplate(
    self,
    "fis-template-inject-unavailable-error",
    description="Inject EC2 API Unavailable Error on the target IAM role.",
    role_arn=importedFISRoleArn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": importedStopConditionArn.to_string(),
        },
    ],
    tags={
        "Name": "EC2 API Unavailable Error",
        "Stackname": self.stack_name,
    },
    actions={
        "instanceActions": unavailableError,
    },
    targets={
        "roleTargets": TargetIAMRole,
    },
)
templateThrottleError = fis.CfnExperimentTemplate(
    self,
    "fis-template-inject-throttle-error",
    description="Inject EC2 API Throttle Error on the target IAM role.",
    role_arn=importedFISRoleArn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": importedStopConditionArn.to_string(),
        },
    ],
    tags={
        "Name": "EC2 API Throttle Error",
        "Stackname": self.stack_name,
    },
    actions={
        "instanceActions": throttleError,
    },
    targets={
        "roleTargets": TargetIAMRole,
    },
)
