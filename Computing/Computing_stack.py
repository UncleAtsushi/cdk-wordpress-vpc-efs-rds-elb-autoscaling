from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
)
from constructs import Construct
import aws_cdk as cdk
from aws_cdk.aws_s3_assets import Asset

class ComputingStack(Stack):

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

        # Import Security Group(EFS)
        wp_sg_efs = ec2.SecurityGroup.from_lookup_by_name(self, "SgEFS",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-efs"
        )

        # Import Security Group(RDS)
        wp_sg_rds = ec2.SecurityGroup.from_lookup_by_name(self, "SgRDS",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-rds"
        )

        # Import Security Group(ELB)
        wp_sg_elb = ec2.SecurityGroup.from_lookup_by_name(self, "SgELB",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-elb"
        )

        # Import Secrurity Group(SSM)
        wp_sg_ssm = ec2.SecurityGroup.from_lookup_by_name(self, "SgSSM",
            vpc=wp_vpc,
            security_group_name="wp-dev-sg-ssm"
        )

        # Import IAM Role(EC2)
        wp_role_ec2 = iam.Role.from_role_name(self, "RoleEC2",
            role_name="wp-dev-role-ec2"
        )
        

        ##############################################
        ############### Server Section ###############
        ##############################################
        # Upload Shell Script(User Data) to s3
        asset = Asset(self, "Asset",
            path="Computing/User_data.sh"
        )

        # Create User Data Instance
        wp_userdata = ec2.UserData.for_linux()

        # Launch Template
        wp_lt = ec2.LaunchTemplate(self, "LaunchTemplate",
            launch_template_name="wp-dev-lt",
            instance_initiated_shutdown_behavior=ec2.InstanceInitiatedShutdownBehavior.TERMINATE,
            security_group=wp_sg_ec2,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE2,
                instance_size=ec2.InstanceSize.MICRO
            ),
            role=wp_role_ec2,
            user_data=wp_userdata,
            machine_image=ec2.AmazonLinuxImage(                       
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            )
            # Set the AMI from EC2 after installed WordPress            
            # machine_image=ec2.MachineImage.generic_linux(
            #     {"us-east-1": "ami-XXXXXXXXXXXXXXXXXX"}
            # )
        )
        # Grant Read to Role of Template
        asset.grant_read(wp_lt.role)

        # Download Shell Script(User Data) to local path
        wp_local_path = wp_userdata.add_s3_download_command(
            bucket=asset.bucket,
            bucket_key=asset.s3_object_key,
            region="us-east-1"
        )

        # Add User Data to Template
        wp_lt.user_data.add_execute_file_command(
            file_path=wp_local_path
        )

        # Auto Scaling Group
        wp_asg = autoscaling.AutoScalingGroup(self, "Asg",
            vpc = wp_vpc,
            auto_scaling_group_name="wp-dev-asg",
            launch_template=wp_lt,
            health_check=autoscaling.HealthCheck.elb(
                grace=cdk.Duration.seconds(30)
            ),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            desired_capacity=1,
            min_capacity=1,
            max_capacity=1
        )

        
        #####################################################
        ############### Load Balancer Section ###############
        #####################################################
        # Application Load Balancer
        wp_alb = elbv2.ApplicationLoadBalancer(self, "Alb",
            vpc=wp_vpc,
            http2_enabled=False,
            ip_address_type=elbv2.IpAddressType.IPV4,
            security_group=wp_sg_elb,
            internet_facing=True,
            load_balancer_name="wp-dev-alb",
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )

        # Target Group
        wp_tg = elbv2.ApplicationTargetGroup(self, "TargetGroup",
            vpc=wp_vpc,
            port=80,
            target_group_name="wp-dev-tg",
            health_check=elbv2.HealthCheck(
                enabled=True,
                protocol=elbv2.Protocol.HTTP,
                port="80",
                path="/readme.html",
                timeout=cdk.Duration.seconds(25), # Defaultis 5
                unhealthy_threshold_count=5 # Default is 2
            ),
            target_type=elbv2.TargetType.INSTANCE
        )
        
        # Add Targets To Auto Scaling Group
        wp_tg.add_target(wp_asg)

        # Add Listner To ELB
        wp_alb.add_listener("AddListener",
            port=80,
            default_target_groups=[wp_tg]
        )


        ######################################################
        ############### Add Allow Rule Section ###############
        ######################################################
        # Add Allow Connection to EC2
        wp_lt.connections.allow_from(wp_sg_elb, ec2.Port.tcp(80)) # Allow HTTP from ALB
        wp_lt.connections.allow_to(wp_sg_ssm, ec2.Port.tcp(443)) # For Acces to EC2 by Sessions Manager
        wp_lt.connections.allow_to_any_ipv4(ec2.Port.tcp(80)) # For EC2 installs some packages by User Data. Disable after installing wordPress.
        wp_lt.connections.allow_to_any_ipv4(ec2.Port.tcp(443)) # For EC2 installs some packages by User Data. Disable after installing wordPress.

        # Add Allow Connection to ELB
        wp_alb.connections.allow_from_any_ipv4(ec2.Port.tcp(80))