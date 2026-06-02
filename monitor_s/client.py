import grpc
import time

from controller_asg.controller import ControllerASG
from generated import monitor_pb2
from generated import monitor_pb2_grpc


controller = ControllerASG()

protected_instances = [
    "i-0d7dad07f45cac19b"
]

while True:
    instances = controller.get_instance_addresses()

    print("\n--- Monitoring Instances ---\n")

    total_cpu = 0
    active_instances = 0

    for instance in instances:
        try:
            channel = grpc.insecure_channel(instance)

            stub = monitor_pb2_grpc.MonitorServiceStub(channel)

            pong = stub.Ping(monitor_pb2.Empty())
            metrics = stub.GetMetrics(monitor_pb2.Empty())

            total_cpu += metrics.cpu
            active_instances += 1

            print(f"Instance: {instance}")
            print(f"Status: {pong.message}")
            print(f"CPU: {metrics.cpu}%")
            print(f"Memory: {metrics.memory}%")
            print("-------------------")

        except Exception as e:
            print(f"Error connecting to {instance}")
            print(e)

    if active_instances > 0:
        average_cpu = total_cpu / active_instances

        print(f"\nAverage CPU: {average_cpu:.2f}%")

        decision = controller.decide(
            average_cpu,
            active_instances
        )

        print(f"Decision: {decision}")

        if decision == "scale_up":
            controller.create_instance()
            time.sleep(60)

        elif decision == "scale_down" and active_instances > 1:
            instances_data = controller.list_instances()

            for instance_data in instances_data:
                if (
                    instance_data["state"] == "running"
                    and instance_data["name"] == "AutoScaledInstance"
                    and instance_data["id"] not in protected_instances
                ):
                    controller.terminate_instance(
                        instance_data["id"]
                    )
                    break

            time.sleep(5)