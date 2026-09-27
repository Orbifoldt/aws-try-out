import os

from aws_cdk import App, CfnOutput, Environment, Stack, Tags
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from dotenv import load_dotenv

load_dotenv()


class MyStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            scope=self,
            id="Vpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="database", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            ],
        )

        app_sg = ec2.SecurityGroup(
            scope=self,
            id="AppSG",
            vpc=vpc,
        )

        instance = ec2.Instance(
            scope=self,
            id="AppInstance",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=app_sg,
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            ssm_session_permissions=True,
        )
        CfnOutput(
            self,
            "AppInstanceId",
            value=instance.instance_id,
            description="EC2 instance id for Session mngr",
        )


app = App()
Tags.of(app).add("Project", "fastapi-learning")
MyStack(
    app,
    "MyStackForLearning",
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)
app.synth()
