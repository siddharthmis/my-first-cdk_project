import aws_cdk_lib as cdk
from constructs import Construct
from aws_cdk_lib.aws_fis as fis

class Ec2InstancesExperiments(Stack):
    def __init__(self, scope: Construct, id: str, props=None):
        super().__init__(scope, id, props)
        importedFISRoleArn = cdk.Fn.import_value("FISIamRoleArn")
        importedStopConditionArn = cdk.Fn.import_value("StopConditionArn")
        vpcId = self.node.try_get_context("vpc_id")
        availabilityZones = Stack.of(self).availability_zones
        randomAvailabilityZone = availabilityZones[random.randint(0, len(availabilityZones)-1)]
        TargetAllInstances = fis.CfnExperimentTemplate.ExperimentTemplateTargetProperty(
            resource_type="aws:ec2:instance",
            selection_mode="ALL",
            resource_tags={
                "FIS-Ready": "true"
            },
            filters=[
                {
                    "path": "Placement.AvailabilityZone",
                    "values": [randomAvailabilityZone]
                },
                {
                    "path": "State.Name",
                    "values": ["running"]
                },
                {
                    "path": "VpcId",
                    "values": [vpcId.toString()],
          },
            ]
        )
        TargetRandomInstance = {
    "resourceType": "aws:ec2:instance",
    "selectionMode": "COUNT(1)",
    "resourceTags": {
        "FIS-Ready": "true"
    },
    "filters": [
        {
            "path": "State.Name",
            "values": ["running"]
        },
        {
            "path": "VpcId",
            "values": [str(vpcId)]
        }
    ]
}

cpuStressAction = {
    "actionId": "aws:ssm:send-command",
    "description": "CPU stress via SSM",
    "parameters": {
        "documentArn": f"arn:aws:ssm:{self.region}::document/AWSFIS-Run-CPU-Stress",
        "documentParameters": json.dumps({
            "DurationSeconds": "120",
            "InstallDependencies": "True",
            "CPU": "0"
        }),
        "duration": "PT2M"
    },
    "targets": {"Instances": "instanceTargets"}
}

stopInstanceAction = {
    "actionId": "aws:ec2:stop-instances",
    "parameters": {
        "startInstancesAfterDuration": "PT5M"
    },
    "targets": {
        "Instances": "instanceTargets"
    }
}

latencySourceAction = {
    "actionId": "aws:ssm:send-command",
    "description": "Latency injection via SSM",
    "parameters": {
        "documentArn": f"arn:aws:ssm:{self.region}::document/AWSFIS-Run-Network-Latency-Sources",
        "documentParameters": json.dumps({
            "DurationSeconds": "120",
            "Interface": "eth0",
            "DelayMilliseconds": "200",
            "JitterMilliseconds": "10",
            "Sources": "www.amazon.com",
            "InstallDependencies": "True",
        }),
        "duration": "PT3M",
    },
    "targets": {"Instances": "instanceTargets"},
}
templateStopStartInstance = fis.CfnExperimentTemplate(
    self,
    "fis-template-stop-instances-in-vpc-az",
    description="Stop and restart all tagged instances in AZ and VPC",
    role_arn=importedFISRoleArn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": importedStopConditionArn.to_string(),
        },
    ],
    tags={
        "Name": "Stop and restart tagged instances in AZ and VPC",
        "Stackname": self.stackName,
    },
    actions={"instanceActions": stopInstanceAction},
    targets={"instanceTargets": TargetAllInstances},
)
templateCPUStress = fis.CfnExperimentTemplate(
    self,
    "fis-template-CPU-stress-random-instances-in-vpc",
    description="Runs CPU stress on random instance",
    role_arn=importedFISRoleArn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": importedStopConditionArn.to_string(),
        },
    ],
    tags={
        "Name": "Stress CPU on random instance in VPC",
        "Stackname": self.stack_name,
    },
    actions={
        "instanceActions": cpuStressAction,
    },
    targets={
        "instanceTargets": TargetRandomInstance,
    },
)

templateLatencySourceInjection = fis.CfnExperimentTemplate(
    self,
    "fis-template-latency-injection-all-instances",
    description="Inject latency to particular domain",
    role_arn=importedFISRoleArn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": importedStopConditionArn.to_string(),
        },
    ],
    tags={
        "Name": "Inject latency on all instances in VPC and random AZ",
        "Stackname": self.stack_name,
    },
    actions={
        "instanceActions": latencySourceAction,
    },
    targets={
        "instanceTargets": TargetAllInstances,
    },
)

