from aws_cdk import aws_fis as fis, aws_iam as iam, core as cdk


class LambdaChaosExperiments(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        importedFISRoleArn = cdk.Fn.import_value("FISIamRoleArn")
        importedStopConditionArn = cdk.Fn.import_value("StopConditionArn")
        importedSSMAPutParameterStoreRoleArn = cdk.Fn.import_value(
            "SSMAPutParameterStoreRoleArn"
        )
        importedPutParameterStoreSSMADocName = cdk.Fn.import_value(
            "PutParameterStoreSSMADocName"
        )
        importedParameterName = self.node.try_get_context("ssm_parameter_name")

        startAutomation = {
            "actionId": "aws:ssm:start-automation-execution",
            "description": "Put config into parameter store to enable Lambda Chaos.",
            "parameters": {
                "documentArn": f"arn:aws:ssm:{self.region}:{self.account}:document/{importedPutParameterStoreSSMADocName}",
                "documentParameters": json.dumps(
                    {
                        "DurationMinutes": "PT1M",
                        "AutomationAssumeRole": str(
                            importedSSMAPutParameterStoreRoleArn
                        ),
                        "ParameterName": str(importedParameterName),
                        "ParameterValue": '{ "delay": 1000, "is_enabled": true, "error_code": 404, "exception_msg": "This is chaos", "rate": 1, "fault_type": "exception"}',
                        "RollbackValue": '{ "delay": 1000, "is_enabled": false, "error_code": 404, "exception_msg": "This is chaos", "rate": 1, "fault_type": "exception"}',
                    }
                ),
                "maxDuration": "PT5M",
            },
        }


putParameter = {
    "actionId": "aws:ssm:put-parameter",
    "description": "Put config into parameter store",
    "parameters": {
        "duration": "PT10M",
        "name": str(importedParameterName),
        "value": '{ "delay": 1000, "is_enabled": true, "error_code": 404, "exception_msg": "This is chaos", "rate": 1, "fault_type": "exception"}',
        "rollbackValue": '{ "delay": 1000, "is_enabled": false, "error_code": 404, "exception_msg": "This is chaos", "rate": 1, "fault_type": "exception"}',
    },
}

# Experiments
template_inject_s3_access_denied = fis.CfnExperimentTemplate(
    self,
    "fis-template-inject-lambda-fault",
    description="Inject faults into Lambda func",
    role_arn=imported_fis_role_arn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": imported_stop_condition_arn.to_string(),
        },
    ],
    tags={
        "Name": "Inject fault to Lambda functions",
        "Stackname": self.stack_name,
    },
    actions={
        "ssmaAction": put_parameter,
    },
    targets={},
)
