from aws_cdk import (
    Stack,
    aws_route53 as route53,
)
from constructs import Construct

class Route53Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Route53
        wp_route53 = route53.HostedZone(self, "Route53",
            zone_name="atsushinotes.work",
        )