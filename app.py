import aws_cdk_lib as cdk
from constructs import Construct
from aws_cdk_lib import StackProps, Stack
from .fis_upload_ssm_docs.ssm_upload_stack import FisSsmDocs
from .fis_role.iam_role_stack import FisRole
from .fis_logs.logs_stack import FisLogs
from .fis_stop_condition.stop_condition_stack import StopCondition
from .fis_experiments.ec2_instance_faults.experiments_stack import (
    Ec2InstancesExperiments,
)
from .fis_experiments.ec2_control_plane_faults.experiments_stack import (
    Ec2ControlPlaneExperiments,
)
from .fis_experiments.nacl_faults.experiments_stack import NaclExperiments
from .fis_experiments.asg_faults.experiments_stack import AsgExperiments
from .fis_experiments.eks_faults.experiments_stack import EksExperiments
from .fis_experiments.security_groups_faults.experiments_stack import (
    SecGroupExperiments,
)
from .fis_experiments.iam_access_faults.experiments_stack import IamAccessExperiments
from .fis_experiments.lambda_faults.experiments_stack import LambdaChaosExperiments


class FIS(Stack):
    def __init__(self, scope: Construct, id: str, props: StackProps = None):
        super().__init__(scope, id, props)
        SSMDocStack = FisSsmDocs(self, "FisSsmDocs")
        LogsStack = FisLogs(self, "FisLogs")
        IamRoleStack = FisRole(self, "FisRole")
        StopConditionStack = StopCondition(self, "StopCond")

        IamRoleStack.add_dependency(LogsStack)


Ec2InstancesExperimentStack = Ec2InstancesExperiments(self, "Ec2InstExp")
Ec2ControlPlaneExperimentsStack = Ec2ControlPlaneExperiments(self, "Ec2APIExp")
NaclExperimentsStack = NaclExperiments(self, "NaclExp")
AsgExperimentsStack = AsgExperiments(self, "AsgExp")
EksExperimentsStack = EksExperiments(self, "EksExp")
SecGroupExperimentsStack = SecGroupExperiments(self, "SecGroupExp")
IamAccessExperimentsStack = IamAccessExperiments(self, "IamAccExp")
LambdaFaultExperimentStack = LambdaChaosExperiments(self, "LambdaExp")

Ec2InstancesExperimentStack.add_dependency(IamRoleStack)
Ec2InstancesExperimentStack.add_dependency(StopConditionStack)
Ec2ControlPlaneExperimentsStack.add_dependency(IamRoleStack)
Ec2ControlPlaneExperimentsStack.add_dependency(StopConditionStack)
NaclExperimentsStack.add_dependency(IamRoleStack)
NaclExperimentsStack.add_dependency(StopConditionStack)
AsgExperimentsStack.add_dependency(IamRoleStack)
AsgExperimentsStack.add_dependency(StopConditionStack)
EksExperimentsStack.add_dependency(IamRoleStack)
EksExperimentsStack.add_dependency(StopConditionStack)
SecGroupExperimentsStack.add_dependency(IamRoleStack)
SecGroupExperimentsStack.add_dependency(StopConditionStack)
IamAccessExperimentsStack.add_dependency(IamRoleStack)
IamAccessExperimentsStack.add_dependency(StopConditionStack)
LambdaFaultExperimentStack.add_dependency(IamRoleStack)
LambdaFaultExperimentStack.add_dependency(StopConditionStack)
