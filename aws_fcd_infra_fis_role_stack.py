from aws_cdk import (
    aws_iam as iam,
    core as cdk,
)

class FisRole(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        importedFISS3BucketArn = cdk.Fn.import_value("fisS3BucketArn")
        fisrole = iam.Role(
            self, "fis-role",
            assumed_by=iam.ServicePrincipal("fis.amazonaws.com"),
            conditions={
                "StringEquals": {
                    "aws:SourceAccount": self.account,
                },
                "ArnLike": {
                    "aws:SourceArn": f"arn:aws:fis:{self.region}:{self.account}:experiment/*",
                },
            },
        )
        fisrole.add_to_policy(
            iam.PolicyStatement(
                resources=["*"],
                actions=["cloudwatch:DescribeAlarms"],
            )
        )
        fisrole.add_to_policy(
            iam.PolicyStatement(
                resources=["*"],
                actions=["ec2:DescribeInstances"],
            )
        )
        fisrole.add_to_policy(
            iam.PolicyStatement(
                resources=["arn:aws:ec2:*:*:instance/*"],
                actions=[
                    "ec2:RebootInstances",
                    "ec2:StopInstances",
                    "ec2:StartInstances",
                    "ec2:TerminateInstances",
                ],
                conditions={
                    "StringEquals": {
                        "aws:ResourceTag/FIS-Ready": "true",
                    },
                },
            )
        )

fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["ec2:SendSpotInstanceInterruptions"],
        resources=["arn:aws:ec2:*:*:instance/*"],
        conditions={
            "StringEquals": {
                "aws:ResourceTag/FIS-Ready": "true"
            }
        }
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["ecs:ListContainerInstances", "ecs:DescribeClusters"],
        resources=["*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["ecs:UpdateContainerInstancesState"],
        resources=["arn:aws:ecs:*:*:container-instance/*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["ec2:DescribeInstances", "eks:DescribeNodegroup"],
        resources=["*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["ec2:TerminateInstances"],
        resources=["arn:aws:ec2:*:*:instance/*"],
        conditions={
            "StringEquals": {
                "aws:ResourceTag/FIS-Ready": "true"
            }
        }
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["rds:DescribeDBInstances", "rds:DescribeDbClusters"],
        resources=["*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["rds:RebootDBInstance"],
        resources=["arn:aws:rds:*:*:db:*"]
    )
)

fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["rds:FailoverDBCluster"],
        resources=["arn:aws:rds:*:*:cluster:*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "ec2:DescribeInstances",
            "ssm:ListCommands",
            "ssm:CancelCommand",
            "ssm:PutParameter"
        ],
        resources=["*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["ssm:StopAutomationExecution", "ssm:GetAutomationExecution"],
        resources=["*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["ssm:StartAutomationExecution"],
        resources=["*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["ssm:SendCommand"],
        resources=["arn:aws:ec2:*:*:instance/*", "arn:aws:ssm:*:*:document/*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["iam:PassRole"],
        resources=["arn:aws:iam::*:role/*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["iam:ListRoles"],
        resources=["*"]
    )
)
fisrole.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "fis:InjectApiInternalError",
            "fis:InjectApiThrottleError",
            "fis:InjectApiUnavailableError",
            "logs:CreateLogDelivery",
            "s3:GetBucketPolicy",
            "s3:PutBucketPolicy",
            "logs:PutResourcePolicy",
            "logs:DescribeResourcePolicies",
            "logs:DescribeLogGroups",
            "firehose:TagDeliveryStream",
            "iam:CreateServiceLinkedRole"
        ],
        resources=[
            "arn:aws:fis:*:*:experiment/*",
            "*",
            importedFISS3BucketArn.to_string(),
        ]
    )
)
cdk.CfnOutput(
    scope=this,
    id="FISIamRoleArn",
    value=fisrole.role_arn,
    description="The Arn of the IAM role",
    export_name="FISIamRoleArn"
)
