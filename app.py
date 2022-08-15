#!/usr/bin/env python3
import os

import aws_cdk as cdk

from Network.Network_stack import NetworkStack
from Storage.Storage_stack import StorageStack
from Database.Database_stack import DatabaseStack
from Computing.Computing_stack import ComputingStack

my_account = "738452829225"
my_region = "ap-northeast-1"
# my_region = "ap-northeast-3"
# my_region = "us-east-1"

envJP = cdk.Environment(account=my_account, region=my_region)
envJP3 = cdk.Environment(account=my_account, region=my_region)
envUS = cdk.Environment(account=my_account, region=my_region)

app = cdk.App()
NetworkStack(app, "Network", env=envJP)
StorageStack(app, "Storage", env=envJP)
DatabaseStack(app, "Database", env=envJP)
ComputingStack(app, "Computing", env=envJP)

# NetworkStack(app, "Network", env=envUS)
# StorageStack(app, "Storage", env=envUS)
# DatabaseStack(app, "Database", env=envUS)
# ComputingStack(app, "Computing", env=envUS)

# NetworkStack(app, "Network", env=envJP3)
# StorageStack(app, "Storage", env=envJP3)
# DatabaseStack(app, "Database", env=envJP3)
# ComputingStack(app, "Computing", env=envJP3)

app.synth()
