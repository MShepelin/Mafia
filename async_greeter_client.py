import asyncio
import logging
import threading

import random

from time import sleep

import grpc
import mafia_pb2
import mafia_pb2_grpc

from gui import ChatGUI

server_channel = 'localhost:50051'
user_id = 0


async def send_message(message):
    global server_channel, user_id
    async with grpc.aio.insecure_channel(server_channel) as channel:
        stub = mafia_pb2_grpc.MafiaServerStub(channel)
        await stub.SendChatMessage(
            mafia_pb2.ChatMessageRequest(user_id=user_id, message=message),
            timeout=10
        )


async def find_game():
    global server_channel, user_id
    async with grpc.aio.insecure_channel(server_channel) as channel:
        stub = mafia_pb2_grpc.MafiaServerStub(channel)
        response = await stub.FindGame(
            mafia_pb2.GameRequest(user_id=user_id)
        )
        print("game id is", response.game_id)
        return response


async def receive_messages(gui):
    global user_id
    async with grpc.aio.insecure_channel(server_channel) as channel:
        stub = mafia_pb2_grpc.MafiaServerStub(channel)
        async for response in stub.ReceiveUpdates(
                    mafia_pb2.UpdatesRequest(user_id=user_id)
                ):

            if response.update_code == mafia_pb2.Update.UpdateStatus.NEW_MESSAGE:
                gui.receive_msg(response.message)


def receive_messages_task(gui):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(receive_messages(gui))
    loop.close()


async def leave_async():
    async with grpc.aio.insecure_channel(server_channel) as channel:
        stub = mafia_pb2_grpc.MafiaServerStub(channel)
        await stub.LeaveGame(mafia_pb2.GameRequest(user_id=user_id))
        print('Left game')


def leave():
    threading.Thread(target=asyncio.run, args=(leave_async,)).start()


async def main():
    global user_id
    logging.basicConfig()

    name = input("Your name:")
    user_id = random.getrandbits(30)

    print("User with id", user_id, "and name", name)
    print('Trying to find game...')
    while True:
        game_response = await find_game()
        if game_response.is_status_ok:
            break
        else:
            print("Not ok, received bad status from server")
        sleep(1)

    try:
        print('Ok, game', game_response.game_id, 'is found')

        gui = ChatGUI(send_message)
        threading.Thread(target=receive_messages_task, args=(gui, )).start()
        gui.win.mainloop()
        leave()
    except:
        leave()

if __name__ == '__main__':
    asyncio.run(main())
