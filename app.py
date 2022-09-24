#!/usr/bin/env python3
import os
import aws_cdk as cdk

from Network.Network_stack import NetworkStack
from Storage.Storage_stack import StorageStack
from Database.Database_stack import DatabaseStack
from Computing.Computing_stack import ComputingStack

my_account = "XXXXXXXXXXXX"
my_region = "us-east-1"

my_env = cdk.Environment(account=my_account, region=my_region)

app = cdk.App()
NetworkStack(app, "Network", env=my_env)
StorageStack(app, "Storage", env=my_env)
DatabaseStack(app, "Database", env=my_env)
ComputingStack(app, "Computing", env=my_env)

app.synth()