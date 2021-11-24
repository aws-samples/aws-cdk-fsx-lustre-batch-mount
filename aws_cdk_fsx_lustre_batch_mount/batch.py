from aws_cdk import core as cdk, aws_ec2 as ec2, aws_ecs as ecs, aws_batch as batch


class BatchStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, vpc, fsx_filesystem, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        fsx_user_data = f"""MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="==MYBOUNDARY=="

--==MYBOUNDARY==
Content-Type: text/cloud-config; charset="us-ascii"

runcmd:
- fsx_directory=/fsx
- amazon-linux-extras install -y lustre2.10
- mkdir -p ${{fsx_directory}}
- mount -t lustre {fsx_filesystem.attr_dns_name}@tcp:/{fsx_filesystem.attr_lustre_mount_name} ${{fsx_directory}}

--==MYBOUNDARY==--
"""

        fsx_lt = ec2.CfnLaunchTemplate(
            self,
            "FsxLT",
            launch_template_name="fsx-lt",
            launch_template_data={
                "userData": cdk.Fn.base64(fsx_user_data),
            },
        )

        batch_env = batch.ComputeEnvironment(
            self,
            "BatchEnv",
            compute_resources=batch.ComputeResources(
                vpc=vpc,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
                instance_types=[ec2.InstanceType("m5.2xlarge")],
                launch_template=batch.LaunchTemplateSpecification(
                    launch_template_name="fsx-lt"
                ),
                minv_cpus=4,
                maxv_cpus=8,
            ),
        )

        batch_env.node.add_dependency(fsx_lt)

        batch.JobQueue(
            self,
            "BatchQueue",
            compute_environments=[
                batch.JobQueueComputeEnvironment(compute_environment=batch_env, order=1)
            ],
            priority=1,
        )

        batch.JobDefinition(
            self,
            "BatchJob",
            container=batch.JobDefinitionContainer(
                image=ecs.ContainerImage.from_registry("amazonlinux"),
                vcpus=1,
                memory_limit_mib=2048,
                volumes=[ecs.Volume(name="fsx", host=ecs.Host(source_path="/fsx"))],
                mount_points=[
                    ecs.MountPoint(
                        container_path="/fsx", source_volume="fsx", read_only=False
                    )
                ],
            ),
            timeout=cdk.Duration.minutes(30),
        )
