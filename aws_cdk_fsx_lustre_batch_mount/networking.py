from aws_cdk import core as cdk, aws_ec2 as ec2


class NetworkingStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(
            self,
            "vpc",
            cidr="10.0.0.0/16",
            nat_gateways=1,
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="private-subnet-1",
                    subnet_type=ec2.SubnetType.PRIVATE,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="public-subnet-1",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
            ],
        )
