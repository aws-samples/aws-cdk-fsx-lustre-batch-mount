#!/usr/bin/env python3
from aws_cdk import core as cdk
from aws_cdk_fsx_lustre_batch_mount.networking import NetworkingStack
from aws_cdk_fsx_lustre_batch_mount.fsx import FSxStack
from aws_cdk_fsx_lustre_batch_mount.batch import BatchStack


app = cdk.App()
networking = NetworkingStack(app, "NetworkingStack")
fsx = FSxStack(app, "FSxStack", networking.vpc)
BatchStack(app, "BatchStack", networking.vpc, fsx.fsx_filesystem)

app.synth()
