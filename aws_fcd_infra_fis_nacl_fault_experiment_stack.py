import aws_cdk_lib as cdk
from constructs import Construct
from aws_cdk_lib.aws_fis as fis

class NaclExperiments(Stack):
    def __init__(self, scope: Construct, id: str, props=None):
        super().__init__(scope, id, props)
        importedFISRoleArn = cdk.Fn.import_value("FISIamRoleArn")
        importedStopConditionArn = cdk.Fn.import_value("StopConditionArn")
        importedSSMANaclRoleArn = cdk.Fn.import_value("SSMANaclRoleArn")
        importedNaclSSMADocName = cdk.Fn.import_value("NaclSSMADocName")
        vpcId = self.node.try_get_context("vpc_id")
        availabilityZones = Stack.of(self).availability_zones
        randomAvailabilityZone = availabilityZones[random.randint(0, len(availabilityZones)-1)] if availabilityZones else None

        # Actions
start_automation = {
    "actionId": "aws:ssm:start-automation-execution",
    "description": "Calling SSMA document to inject faults in the NACLS of a particular AZ.",
    "parameters": {
        "documentArn": f"arn:aws:ssm:{self.region}:{self.account}:document/{importedNaclSSMADocName}",
        "documentParameters": json.dumps({
            "AvailabilityZone": str(randomAvailabilityZone),
            "VPCId": str(vpcId),
            "DurationMinutes": "PT1M",
            "AutomationAssumeRole": str(importedSSMANaclRoleArn),
        }),
        "maxDuration": "PT2M",
    },
}

# Experiments
template_nacl = fis.CfnExperimentTemplate(
    self,
    "fis-template-inject-nacl-fault",
    description="Deny network traffic in subnets of a particular AZ. Rollback on Cancel or Failure.",
    role_arn=str(importedFISRoleArn),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": str(importedStopConditionArn),
        },
    ],
    tags={
        "Name": "Deny network traffic in subnets of a particular AZ",
        "Stackname": self.stackName,
    },
    actions={
        "ssmaAction": start_automation,
    },
    targets={},
)
