from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_efs as efs
)
from constructs import Construct
import aws_cdk as cdk

class StorageStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ##############################################
        ############### Import Section ###############
        ##############################################
        # Import VPC
        wp_vpc = ec2.Vpc.from_lookup(self, "Vpc",
            vpc_name="wp-dev-vpc"
        )

        # Import Security Group(EFS)
        wp_sg_efs = ec2.SecurityGroup.from_lookup_by_name(self, "SgEFS",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-efs"
        )

        # Import Security Group(EC2)
        wp_sg_ec2 = ec2.SecurityGroup.from_lookup_by_name(self, "SgEC2",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-ec2"
        )
        

        ###############################################
        ############### Storage Section ###############
        ###############################################
        # EFS File System
        wp_efs = efs.FileSystem(self, "Efs",
            vpc=wp_vpc,
            encrypted=True,
            file_system_name="wp-dev-efs",
            security_group=wp_sg_efs,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            removal_policy=cdk.RemovalPolicy.DESTROY
        )


        ######################################################
        ############### Add Allow Rule Section ###############
        ######################################################
        # Add Allow Connection to EFS
        wp_efs.connections.allow_from(wp_sg_ec2, ec2.Port.tcp(2049))