import json
import boto3


class ControllerASG:

    def __init__(self, config_path="config/settings.json"):

        with open(config_path, "r") as file:
            self.config = json.load(file)

        self.ec2 = boto3.client(
            "ec2",
            region_name=self.config["region"]
        )

    def decide(self, average_cpu, active_instances):

        min_instances = self.config["min_instances"]
        max_instances = self.config["max_instances"]

        scale_up_threshold = self.config["scale_up_threshold"]
        scale_down_threshold = self.config["scale_down_threshold"]

        if (
            average_cpu > scale_up_threshold
            and active_instances < max_instances
        ):
            return "scale_up"

        if (
            average_cpu < scale_down_threshold
            and active_instances > min_instances
        ):
            return "scale_down"

        return "keep"

    def list_instances(self):

        response = self.ec2.describe_instances()

        instances = []

        for reservation in response["Reservations"]:

            for instance in reservation["Instances"]:

                if instance["State"]["Name"] == "running":
                    instances.append({
                        "id": instance["InstanceId"],
                        "state": instance["State"]["Name"],
                        "type": instance["InstanceType"],
                        "public_ip": instance.get(
                            "PublicIpAddress",
                            None
                        )
                    })

        return instances
    
    def get_instance_addresses(self):

        instances = self.list_instances()

        addresses = []

        for instance in instances:

            if instance["public_ip"]:

                addresses.append(
                    f"{instance['public_ip']}:50051"
                )

        return addresses

    def create_instance(self):

        response = self.ec2.run_instances(
            ImageId=self.config["ami_id"],
            InstanceType=self.config["instance_type"],
            MinCount=1,
            MaxCount=1,
            KeyName=self.config["key_name"],
            SecurityGroupIds=[
                self.config["security_group_id"]
            ],
            SubnetId=self.config["subnet_id"],

            UserData="""#!/bin/bash
            cd /home/ubuntu/proyecto2-autoscaling
            source venv/bin/activate
            PYTHONPATH=. nohup python monitor_c/server.py 50051 > monitorc.log 2>&1 &
            """,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "AutoScaledInstance"
                        }
                    ]
                }
            ]
        )

        instance_id = response["Instances"][0]["InstanceId"]

        print(
            f"Created instance: {instance_id}"
        )

        return instance_id


    def terminate_instance(self, instance_id):

        self.ec2.terminate_instances(
            InstanceIds=[
                instance_id
            ]
        )

        print(
            f"Terminated instance: {instance_id}"
        )