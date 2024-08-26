from aws_cdk import (
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_lambda_event_sources as event_sources,
    aws_events as events,
    aws_events_targets as targets,
    custom_resources as cr,
    core,
)

import os

class FreeStaticIpStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "Vpc", nat_gateways=0)

        sg = ec2.SecurityGroup(self, "SecurityGroup", vpc=vpc)

        func = _lambda.Function(
            self,
            "TestFunc",
            runtime=_lambda.Runtime.NODEJS_18_X,
            handler="handler.handler",
            code=_lambda.Code.from_asset(os.path.join(os.path.dirname(__file__), "./handler")),
            vpc=vpc,
            allow_public_subnet=True,
            vpc_subnets=ec2.SubnetSelection(subnets=vpc.public_subnets),
            security_groups=[sg],
        )

        for subnet in vpc.public_subnets:
            custom_resource = cr.AwsCustomResource(
                self,
                f"CustomResource{subnet.subnet_id}",
                on_update={
                    "physical_resource_id": cr.PhysicalResourceId.of(f"{sg.security_group_id}-{subnet.subnet_id}-CustomResource"),
                    "service": "EC2",
                    "action": "describeNetworkInterfaces",
                    "parameters": {
                        "Filters": [
                            {"Name": "interface-type", "Values": ["lambda"]},
                            {"Name": "group-id", "Values": [sg.security_group_id]},
                            {"Name": "subnet-id", "Values": [subnet.subnet_id]},
                        ],
                    },
                },
                policy=cr.AwsCustomResourcePolicy.from_sdk_calls(resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
            )

            custom_resource.node.add_dependency(func)

            eip = ec2.CfnEIP(self, f"EIP{subnet.subnet_id}", domain="vpc")

            ec2.CfnEIPAssociation(
                self,
                f"EIPAssociation{subnet.subnet_id}",
                network_interface_id=custom_resource.get_response_field("NetworkInterfaces.0.NetworkInterfaceId"),
                allocation_id=eip.attr_allocation_id,
            )

            core.CfnOutput(self, f"ElasticIP{subnet.subnet_id}", value=eip.attr_public_ip)

        # prevent the lambda function from losing its ENI
        events.Rule(
            self,
            "LambdaWeeklyTriggerRule",
            schedule=events.Schedule.cron(minute="0", hour="10", week_day="SUN,WED"),
            targets=[targets.LambdaFunction(func)],
        )
