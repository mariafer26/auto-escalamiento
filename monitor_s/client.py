import grpc
import time

from generated import monitor_pb2
from generated import monitor_pb2_grpc


instances = [
     "54.159.119.132:50051"
]


while True:

    print("\n--- Monitoring Instances ---\n")

    total_cpu = 0
    active_instances = 0

    for instance in instances:

        try:

            channel = grpc.insecure_channel(
                instance
            )

            stub = monitor_pb2_grpc.MonitorServiceStub(
                channel
            )

            pong = stub.Ping(
                monitor_pb2.Empty()
            )

            metrics = stub.GetMetrics(
                monitor_pb2.Empty()
            )

            total_cpu += metrics.cpu
            active_instances += 1

            print(
                f"Instance: {instance}"
            )

            print(
                f"Status: {pong.message}"
            )

            print(
                f"CPU: {metrics.cpu}%"
            )

            print(
                f"Memory: {metrics.memory}%"
            )

            print("-------------------")

        except Exception as e:

            print(
                f"Error connecting to {instance}"
            )

            print(e)

    if active_instances > 0:

        average_cpu = total_cpu / active_instances

        print(
            f"\nAverage CPU: {average_cpu:.2f}%"
        )

        if average_cpu > 75:

            print(
                "Decision: scale up - create new instance"
            )

        elif average_cpu < 25:

            print(
                "Decision: scale down - remove instance"
            )

        else:

            print(
                "Decision: keep current instances"
            )

    time.sleep(5)