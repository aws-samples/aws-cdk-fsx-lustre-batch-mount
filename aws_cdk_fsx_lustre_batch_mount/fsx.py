from aws_cdk import (
    core as cdk,
    aws_ec2 as ec2,
    aws_fsx as fsx,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
)


class FSxStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        fsx_repository_bucket = s3.Bucket(
            self,
            "FSxRepositoryBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        s3_deployment.BucketDeployment(
            self,
            "FSxBucketDeployment",
            destination_bucket=fsx_repository_bucket,
            sources=[
                s3_deployment.Source.asset(
                    path="aws_cdk_fsx_lustre_batch_mount/assets/"
                )
            ],
            retain_on_delete=False,
        )

        fsx_security_group = ec2.SecurityGroup(
            self,
            "FsxSg",
            vpc=vpc,
            allow_all_outbound=True,
            security_group_name="fsx-lustre-sg",
        )

        fsx_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(988),
            description="FSx Lustre",
        )

        self.fsx_filesystem = fsx.CfnFileSystem(
            self,
            "Fsx",
            file_system_type="LUSTRE",
            storage_capacity=1200,
            subnet_ids=[
                vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnet_ids[0]
            ],
            security_group_ids=[fsx_security_group.security_group_id],
            tags=[cdk.CfnTag(key="Name", value="fsx-lustre")],
            lustre_configuration=fsx.CfnFileSystem.LustreConfigurationProperty(
                auto_import_policy="NEW_CHANGED",
                deployment_type="PERSISTENT_1",
                per_unit_storage_throughput=50,
                data_compression_type="LZ4",
                import_path=f"s3://{fsx_repository_bucket.bucket_name}/",
                export_path=f"s3://{fsx_repository_bucket.bucket_name}/",
            ),
        )
