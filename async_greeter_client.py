import asyncio
import logging

import grpc
import mafia_pb2
import mafia_pb2_grpc


async def run() -> None:
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = mafia_pb2_grpc.MafiaServerStub(channel)
        response = await stub.SendChatMessage(
            mafia_pb2.ChatMessageRequest(user_id=4, message="Hello, server, how are u?")
        )
    print("Client received: ", response.is_status_ok)


if __name__ == '__main__':
    logging.basicConfig()
    asyncio.run(run())
