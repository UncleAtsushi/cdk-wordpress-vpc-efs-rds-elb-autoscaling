from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam
)
from constructs import Construct

class NetworkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ###############################################
        ############### Network Section ###############
        ###############################################
        # VPC & Subnet
        wp_vpc = ec2.Vpc(self, "Vpc",
            vpc_name="wp-dev-vpc",
            cidr="10.0.0.0/16",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="wp-dev-public",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="wp-dev-private-with-nat",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
                ),
                ec2.SubnetConfiguration(
                    name="wp-dev-private-isolated",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                )
            ]
        )


        ######################################################
        ############### Security Group Section ###############
        ######################################################
        # Security Group(ELB)
        wp_sg_elb = ec2.SecurityGroup(self, "SgELB",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-elb",
            description="Security Group for ELB",
            allow_all_outbound=False
        )
        
        # Security Group(EC2)
        wp_sg_ec2 = ec2.SecurityGroup(self, "SgEC2",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-ec2",
            description="Security Group for EC2",
            allow_all_outbound=False
        )

        # Security Group(EFS)
        wp_sg_efs = ec2.SecurityGroup(self, "SgEFS",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-efs",
            description="Security Group for EFS",
            allow_all_outbound=False
        )

        # Security Group(RDS)
        wp_sg_rds = ec2.SecurityGroup(self, "SgRDS",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-rds",
            description="Security Group for RDS",
            allow_all_outbound=False
        )

        # Security Group(SSM)
        wp_sg_ssm = ec2.SecurityGroup(self, "SgSSM",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-ssm",
            description="Security Group for SSM",
            allow_all_outbound=False
        )


        ################################################
        ############### Endpoint Section ###############
        ################################################
        # SSM Endpoint
        ec2.InterfaceVpcEndpoint(self, "SSMEndpoint",
            vpc=wp_vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            security_groups=[wp_sg_ssm],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
        )
        # SSM_MESSAGES Endpoint
        ec2.InterfaceVpcEndpoint(self, "SSM_MESSAGESEndpoint",
            vpc=wp_vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
            security_groups=[wp_sg_ssm],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
        )
        # EC2_MESSAGES Endpoint
        ec2.InterfaceVpcEndpoint(self, "EC2_MESSAGESEndpoint",
            vpc=wp_vpc,
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
            security_groups=[wp_sg_ssm],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
        )


        ###########################################
        ############### IAM Section ###############
        ###########################################
        # Role(EC2)
        wp_role_ec2 = iam.Role(self, "RoleEC2",
            role_name="wp-dev-role-ec2",
            description="Role for EC2",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )

        # Add Policy To Role(EC2)
        wp_role_ec2.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="AmazonSSMManagedInstanceCore")
        )
        wp_role_ec2.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="AmazonElasticFileSystemReadOnlyAccess")
        )
        wp_role_ec2.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="SecretsManagerReadWrite")
        )
        wp_role_ec2.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="ElasticLoadBalancingReadOnly")
        )