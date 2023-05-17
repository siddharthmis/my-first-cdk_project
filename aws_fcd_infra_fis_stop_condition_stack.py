from aws_cdk import (
    aws_cloudwatch as cw,
    core as cdk,
)
from aws_cdk.core import (
    Construct,
    Stack,
    StackProps,
)


class StopCondition(Stack):
    def __init__(self, scope: Construct, id: str, props: StackProps = None):
        super().__init__(scope, id, props)
        # FIS Stop Condition
        alarm = cw.Alarm(
            self,
            "cw-alarm",
            alarm_name="NetworkInAbnormal",
            metric=cw.Metric(
                metric_name="NetworkIn",
                namespace="AWS/EC2",
            ).with_period(cdk.Duration.seconds(60)),
            threshold=10,
            evaluation_periods=1,
            treat_missing_data=cw.TreatMissingData.NOT_BREACHING,
            comparison_operator=cw.ComparisonOperator.LESS_THAN_THRESHOLD,
            datapoints_to_alarm=1,
        )
        cdk.CfnOutput(
            self,
            "StopConditionArn",
            value=alarm.alarm_arn,
            description="The Arn of the Stop-Conditioin CloudWatch Alarm",
            export_name="StopConditionArn",
        )
