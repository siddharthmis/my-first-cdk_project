from aws_cdk import (
    aws_fis as fis,
    core as cdk,
)
from aws_cdk.core import (
    Construct,
    Stack,
    StackProps,
)

class EksExperiments(Stack):
    def __init__(self, scope: Construct, id: str, props: StackProps = None):
        super().__init__(scope, id, props)
        # Import FIS Role and Stop Condition
        imported_fis_role_arn = cdk.Fn.import_value("FISIamRoleArn")
        imported_stop_condition_arn = cdk.Fn.import_value("StopConditionArn")
        eks_cluster_name = self.node.try_get_context("eks_cluster_name")
        # Targets
        target_eks_cluster = fis.CfnExperimentTemplate.ExperimentTemplateTargetProperty(
            resource_type="aws:eks:nodegroup",
            selection_mode="ALL",
            resource_tags={
                "eksctl.cluster.k8s.io/v1alpha1/cluster-name": str(eks_cluster_name),
            },
        )
        # Actions
        terminate_node_group_instance = fis.CfnExperimentTemplate.ExperimentTemplateActionProperty(
            action_id="aws:eks:terminate-nodegroup-instances",
            parameters={
                "instanceTerminationPercentage": "50",
            },
            targets={
                "Nodegroups": "nodeGroupTarget",
            },
        )

        # Experiments
template_eks_terminate_node_group = fis.CfnExperimentTemplate(
    self,
    "fis-eks-terminate-node-group",
    description="Terminate 50 per cent instances on the EKS target node group.",
    role_arn=imported_fis_role_arn.to_string(),
    stop_conditions=[
        {
            "source": "aws:cloudwatch:alarm",
            "value": imported_stop_condition_arn.to_string(),
        },
    ],
    tags={
        "Name": "Terminate 50 per cent instances on the EKS target node group",
        "Stackname": self.stack_name,
    },
    actions={
        "nodeGroupActions": terminate_node_group_instance,
    },
    targets={
        "nodeGroupTarget": target_eks_cluster,
    },
)


