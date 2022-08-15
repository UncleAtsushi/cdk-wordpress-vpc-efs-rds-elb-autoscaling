from aws_cdk import (
    Stack,
    aws_route53 as route53,
    aws_certificatemanager as acm,
)
from constructs import Construct
import aws_cdk as cdk

class AcmJPStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Obtain Route53
        wp_route53 = route53.HostedZone.from_lookup(self, "Route53",
            domain_name="atsushinotes.work"
        )
        
        # ACM
        wp_acm = acm.Certificate(self, "AcmJP",
            domain_name="*.atsushinotes.work",
            validation=acm.CertificateValidation.from_dns(wp_route53)
        )

        # Output Certificate ARN
        cdk.CfnOutput(self, "OutputAcmJPArn",
            value=wp_acm.certificate_arn,
            export_name="AcmJPArn"
        )