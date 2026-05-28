from concurrent import futures
import grpc
import random
import sys

from generated import monitor_pb2
from generated import monitor_pb2_grpc


class MonitorService(
    monitor_pb2_grpc.MonitorServiceServicer
):

    def Ping(self, request, context):

        return monitor_pb2.Pong(
            message="pong"
        )

    def GetMetrics(self, request, context):

        return monitor_pb2.Metrics(
            cpu=random.randint(10, 90),
            memory=random.randint(20, 80)
        )


def serve():

    port = sys.argv[1] if len(sys.argv) > 1 else "50051"

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    monitor_pb2_grpc.add_MonitorServiceServicer_to_server(
        MonitorService(),
        server
    )

    server.add_insecure_port(
        f"[::]:{port}"
    )

    server.start()

    print(
        f"MonitorC running on port {port}"
    )

    server.wait_for_termination()


serve()