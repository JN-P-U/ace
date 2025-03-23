# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import warnings

import grpc
from src.protos import stt_pb2 as stt__pb2

GRPC_GENERATED_VERSION = "1.71.0"
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower

    _version_not_supported = first_version_is_lower(
        GRPC_VERSION, GRPC_GENERATED_VERSION
    )
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f"The grpc package installed is at version {GRPC_VERSION},"
        + f" but the generated code in stt_pb2_grpc.py depends on"
        + f" grpcio>={GRPC_GENERATED_VERSION}."
        + f" Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}"
        + f" or downgrade your generated code using grpcio-tools<={GRPC_VERSION}."
    )


class STTServiceStub(object):
    """STT 기능 제공"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Start = channel.unary_unary(
            "/stt.STTService/Start",
            request_serializer=stt__pb2.StartRequest.SerializeToString,
            response_deserializer=stt__pb2.StartResponse.FromString,
            _registered_method=True,
        )
        self.Stop = channel.unary_unary(
            "/stt.STTService/Stop",
            request_serializer=stt__pb2.StopRequest.SerializeToString,
            response_deserializer=stt__pb2.StopResponse.FromString,
            _registered_method=True,
        )
        self.StreamRecognized = channel.stream_stream(
            "/stt.STTService/StreamRecognized",
            request_serializer=stt__pb2.StreamRecognizedRequest.SerializeToString,
            response_deserializer=stt__pb2.StreamRecognizedResponse.FromString,
            _registered_method=True,
        )


class STTServiceServicer(object):
    """STT 기능 제공"""

    def Start(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Stop(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def StreamRecognized(self, request_iterator, context):
        """요청도 스트리밍 형태로 변경:"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_STTServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Start": grpc.unary_unary_rpc_method_handler(
            servicer.Start,
            request_deserializer=stt__pb2.StartRequest.FromString,
            response_serializer=stt__pb2.StartResponse.SerializeToString,
        ),
        "Stop": grpc.unary_unary_rpc_method_handler(
            servicer.Stop,
            request_deserializer=stt__pb2.StopRequest.FromString,
            response_serializer=stt__pb2.StopResponse.SerializeToString,
        ),
        "StreamRecognized": grpc.stream_stream_rpc_method_handler(
            servicer.StreamRecognized,
            request_deserializer=stt__pb2.StreamRecognizedRequest.FromString,
            response_serializer=stt__pb2.StreamRecognizedResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "stt.STTService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers("stt.STTService", rpc_method_handlers)


# This class is part of an EXPERIMENTAL API.
class STTService(object):
    """STT 기능 제공"""

    @staticmethod
    def Start(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/stt.STTService/Start",
            stt__pb2.StartRequest.SerializeToString,
            stt__pb2.StartResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def Stop(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/stt.STTService/Stop",
            stt__pb2.StopRequest.SerializeToString,
            stt__pb2.StopResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def StreamRecognized(
        request_iterator,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            "/stt.STTService/StreamRecognized",
            stt__pb2.StreamRecognizedRequest.SerializeToString,
            stt__pb2.StreamRecognizedResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )
