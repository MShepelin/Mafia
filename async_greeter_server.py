import asyncio
import logging
from threading import Lock

import grpc
import mafia_pb2
import mafia_pb2_grpc

from time import sleep
from queue import Queue


class MafiaServer(mafia_pb2_grpc.MafiaServerServicer):
    def __init__(self):
        self.user_to_stream = {}
        self.change_lock = Lock()

    async def LeaveGame(
            self, request: mafia_pb2.GameRequest,
            context: grpc.aio.ServicerContext):
        with self.change_lock:
            self.user_to_stream.pop(request.user_id)
            for user_id, stream in self.user_to_stream.items():
                stream.put(mafia_pb2.Update(
                    message="User " + str(request.user_id) + " left\n",
                    update_code=mafia_pb2.Update.UpdateStatus.NEW_MESSAGE)
                )


    async def SendChatMessage(
            self, request: mafia_pb2.ChatMessageRequest,
            context: grpc.aio.ServicerContext) -> mafia_pb2.RequestProcessStatus:
        print("user", request.user_id, "sent", request.message, end="")

        with self.change_lock:
            for user_id, stream in self.user_to_stream.items():
                stream.put(mafia_pb2.Update(
                    message=str(request.user_id) + ":" + request.message + "\n",
                    update_code=mafia_pb2.Update.UpdateStatus.NEW_MESSAGE)
                )

        return mafia_pb2.RequestProcessStatus(is_status_ok=True)

    async def FindGame(
            self, request: mafia_pb2.GameRequest,
            context: grpc.aio.ServicerContext) -> mafia_pb2.RequestProcessStatus:
        with self.change_lock:
            if request.user_id in self.user_to_stream:
                return mafia_pb2.RequestProcessStatus(is_status_ok=False)

            users_keys = list(self.user_to_stream.keys())

            self.user_to_stream[request.user_id] = Queue()
            self.user_to_stream[request.user_id].put(mafia_pb2.Update(
                message="Users:" + str(users_keys) + "\n",
                update_code=mafia_pb2.Update.UpdateStatus.NEW_MESSAGE)
            )
            for user_id, stream in self.user_to_stream.items():
                stream.put(mafia_pb2.Update(
                    message="Got new user with id " + str(request.user_id) + "\n",
                    update_code=mafia_pb2.Update.UpdateStatus.NEW_MESSAGE)
                )

        game_id = 0
        return mafia_pb2.GameSearchResponse(is_status_ok=True, game_id=game_id)

    async def ReceiveUpdates(
            self, request: mafia_pb2.UpdatesRequest,
            context: grpc.aio.ServicerContext):

        while True:
            sleep(0.1)

            with self.change_lock:
                length = self.user_to_stream[request.user_id].qsize()

            if length > 0:
                with self.change_lock:
                    message = self.user_to_stream[request.user_id].get().message

                yield mafia_pb2.Update(
                       message=str(length) if length == 0 else message,
                       update_code=mafia_pb2.Update.UpdateStatus.NEW_MESSAGE
                )
            else:
                yield mafia_pb2.Update(
                    message="",
                    update_code=mafia_pb2.Update.UpdateStatus.NOTHING
                )


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
