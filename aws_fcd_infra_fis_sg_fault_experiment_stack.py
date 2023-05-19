import boto3

class SecGroupExperiments(cdk.Stack):
    def __init__(self, scope: Construct, id: str, props=None):
        super().__init__(scope, id, props)
        # Import FIS Role and Stop Condition
        importedFISRoleArn = cdk.Fn.import_value("FISIamRoleArn")
        importedSSMASecGroupRoleArn = cdk.Fn.import_value("SSMASecGroupRoleArn")
        importedStopConditionArn = cdk.Fn.import_value("StopConditionArn")
        importedSecGroupSSMADocName = cdk.Fn.import_value("SecGroupSSMADocName")
        securityGroupId = self.node.try_get_context("security_group_id")
        # Actions
        start_automation = {
            "actionId": "aws:ssm:start-automation-execution",
            "description": "Calling SSMA document to inject faults in a particular security group (open SSH to 0.0.0.0/0)",
            "parameters": {
                "documentArn": f"arn:aws:ssm:{self.region}:{self.account}:document/{importedSecGroupSSMADocName}",
                "documentParameters": json.dumps({
                    "DurationMinutes": "PT1M",
                    "SecurityGroupId": securityGroupId,
                    "AutomationAssumeRole": importedSSMASecGroupRoleArn,
                }),
                "maxDuration": "PT5M",
            },
        }

        # Experiments
template_sec_group = fis.CfnExperimentTemplate(
    self,
    "fis-template-inject-secgroup-fault",
    description="Experiment to test response to a change in security group ingress rule (open SSH to 0.0.0.0/0)",
    role_arn=imported_fis_role_arn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": imported_stop_condition_arn.to_string(),
        },
    ],
    tags={
        "Name": "Security Group ingress open SSH to all",
        "Stackname": self.stack_name,
    },
    actions={
        "ssmaAction": start_automation,
    },
    targets={},
)
