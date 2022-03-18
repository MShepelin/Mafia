load("//bazel:python_rules.bzl", "py_grpc_library", "py_proto_library")

licenses(["notice"])

package(default_visibility = ["//visibility:public"])

py_proto_library(
    name = "mafia_py_pb2",
    deps = [":mafia_proto"],
)

py_grpc_library(
    name = "mafia_py_pb2_grpc",
    srcs = [":mafia_proto"],
    deps = [":mafia_py_pb2"],
)
