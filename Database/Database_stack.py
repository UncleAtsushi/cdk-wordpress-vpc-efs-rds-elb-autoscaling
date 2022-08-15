from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager
)
from constructs import Construct
import aws_cdk as cdk

class DatabaseStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ##############################################
        ############### Import Section ###############
        ##############################################
        # Import VPC
        wp_vpc = ec2.Vpc.from_lookup(self, "Vpc",
            vpc_name="wp-dev-vpc"
        )

        # Import Security Group(EC2)
        wp_sg_ec2 = ec2.SecurityGroup.from_lookup_by_name(self, "SgEC2",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-ec2"
        )

        # Import Security Group(RDS)
        wp_sg_rds = ec2.SecurityGroup.from_lookup_by_name(self, "SgRDS",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-rds"
        )


        ################################################
        ############### Database Section ###############
        ################################################
        # DB Subnet Group
        wp_dbsubnet = rds.SubnetGroup(self, "DBSubnet",
            vpc=wp_vpc,
            description="Subnet Group for RDS",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            subnet_group_name="wp-dev-dbsubnet",
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            )
        )

        # DB Instance Engine
        wp_dbengine = rds.DatabaseInstanceEngine.mysql(
            version=rds.MysqlEngineVersion.VER_5_7_37
        )
        
        # Database Credential
        wp_secret_rds = rds.DatabaseSecret(self, "RdsSecret",
            username="root",
            secret_name="wp-dev-secret-rds"
        )
        wp_credentials_rds = rds.Credentials.from_secret(
            secret=wp_secret_rds
        )

        # RDS
        wp_rds = rds.DatabaseInstance(self, "Rds",
            vpc=wp_vpc,
            engine=wp_dbengine,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            instance_identifier="wp-dev-rds",
            multi_az=True,
            publicly_accessible=False,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            security_groups=[wp_sg_rds],
            subnet_group=wp_dbsubnet,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            credentials=wp_credentials_rds,
            allocated_storage=20,
            backup_retention=Duration.days(0),
            delete_automated_backups=True,
            deletion_protection=False,
            port=3306
        )


        ######################################################
        ############### Add Allow Rule Section ###############
        ######################################################
        # Add Allow Connection to RDS
        wp_rds.connections.allow_from(wp_sg_ec2, ec2.Port.tcp(3306))