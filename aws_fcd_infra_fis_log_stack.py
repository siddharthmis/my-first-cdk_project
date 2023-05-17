from aws_cdk import (
    aws_logs as logs,
    aws_s3 as s3,
    core
)

class FisLogs(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Cloudwatch logGroup
        fis_log_group = logs.LogGroup(self, 'fisLogGroup')

        # S3 bucket for FIS logs
        fis_s3_bucket = s3.Bucket(self, 'fisS3Bucket')

        core.CfnOutput(self, 'fisLogGroupArn',
            value=fis_log_group.log_group_arn,
            description='The Arn of the logGroup',
            export_name='fisLogGroupArn'
        )

        core.CfnOutput(self, 'fisS3BucketArn',
            value=fis_s3_bucket.bucket_arn,
            description='The Arn of the S3 bucket',
            export_name='fisS3BucketArn'
        )

        core.CfnOutput(self, 'fisS3BucketName',
            value=fis_s3_bucket.bucket_name,
            description='The name of the S3 bucket',
            export_name='fisS3BucketName'
        )
