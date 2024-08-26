#!/usr/bin/env python3
import aws_cdk as cdk
from free_static_ip_stack import FreeStaticIpStack

app = cdk.App()
FreeStaticIpStack(app, "FreeStaticIpStack", 
    # Uncomment the following line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    # env={'account': os.getenv('CDK_DEFAULT_ACCOUNT'), 'region': os.getenv('CDK_DEFAULT_REGION')},

    # Uncomment the following line if you know exactly what Account and Region you
    # want to deploy the stack to.
    # env={'account': '123456789012', 'region': 'us-east-1'},

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

app.synth()