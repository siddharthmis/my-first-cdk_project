import cdk from "aws-cdk-lib"
from constructs import Construct
from aws_cdk_lib.aws_fis as fis
from aws_cdk_lib.aws_ec2 as ec2

class AsgExperiments(Stack):
    def __init__(self, scope: Construct, id: str, props: StackProps = None):
        super().__init__(scope, id, props)
        importedFISRoleArn = cdk.Fn.import_value("FISIamRoleArn")
        importedStopConditionArn = cdk.Fn.import_value("StopConditionArn")
        asgName = self.node.try_get_context("asg_name")
        availabilityZones = self.availability_zones
        randomAvailabilityZone = availabilityZones[int(random() * len(availabilityZones))]
        TargetAllInstancesASG = fis.CfnExperimentTemplate.ExperimentTemplateTargetProperty(
            resource_type="aws:ec2:instance",
            selection_mode="ALL",
            resource_tags={
                "aws:autoscaling:groupName": asgName,
            },
            filters=[
                {
                    "path": "State.Name",
                    "values": ["running"],
                },
            ],
        )

        TargetAllInstancesASGAZ = {
    "resourceType": "aws:ec2:instance",
    "selectionMode": "ALL",
    "resourceTags": {
        "aws:autoscaling:groupName": str(asgName),
    },
    "filters": [
        {
            "path": "State.Name",
            "values": ["running"],
        },
        {
            "path": "Placement.AvailabilityZone",
            "values": [randomAvailabilityZone],
        },
    ],
}

terminateInstanceAction = {
    "actionId": "aws:ec2:terminate-instances",
    "parameters": {},
    "targets": {
        "Instances": "instanceTargets",
    },
}

cpuStressAction = {
    "actionId": "aws:ssm:send-command",
    "description": "CPU stress via SSM",
    "parameters": {
        "documentArn": f"arn:aws:ssm:{self.region}::document/AWSFIS-Run-CPU-Stress",
        "documentParameters": json.dumps({
            "DurationSeconds": "120",
            "InstallDependencies": "True",
            "CPU": "0",
        }),
        "duration": "PT2M",
    },
    "targets": {"Instances": "instanceTargets"},
}

templateTerminateInstanceASGAZ = fis.CfnExperimentTemplate(
    self,
    "fis-template-stop-instances-in-asg-az",
    description="Terminate all instances of ASG in random AZ",
    role_arn=importedFISRoleArn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": importedStopConditionArn.to_string(),
        },
    ],
    tags={
        "Name": "Terminate instances of ASG in random AZ",
        "Stackname": self.stack_name,
    },
    actions={
        "instanceActions": terminateInstanceAction,
    },
    targets={
        "instanceTargets": TargetAllInstancesASGAZ,
    },
)

templateCPUStress = fis.CfnExperimentTemplate(
    self,
    "fis-template-CPU-stress-random-instances-in-vpc",
    description="Runs CPU stress on all instances of an ASG",
    role_arn=importedFISRoleArn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": importedStopConditionArn.to_string(),
        },
    ],
    tags={
        "Name": "CPU Stress to all instances of ASG",
        "Stackname": self.stack_name,
    },
    actions={
        "instanceActions": cpuStressAction,
    },
    targets={
        "instanceTargets": TargetAllInstancesASG,
    },
)
