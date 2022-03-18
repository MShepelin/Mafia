# Copyright 2020 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python AsyncIO implementation of the GRPC helloworld.Greeter server."""

import asyncio
import logging

import grpc
import mafia_pb2
import mafia_pb2_grpc


class MafiaServer(mafia_pb2_grpc.MafiaServerServicer):
    async def SendChatMessage(
            self, request: mafia_pb2.ChatMessageRequest,
            context: grpc.aio.ServicerContext) -> mafia_pb2.RequestProcessStatus:
        print("user", request.user_id, "sent", request.message)
        return mafia_pb2.RequestProcessStatus(is_status_ok=True)


async def serve() -> None:
    server = grpc.aio.server()
    mafia_pb2_grpc.add_MafiaServerServicer_to_server(MafiaServer(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
