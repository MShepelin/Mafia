import tkinter
from tkinter import scrolledtext

import asyncio
import threading


class ChatGUI:
    def __init__(self, on_send):
        msg = tkinter.Tk()
        msg.withdraw()

        self.on_send = on_send

        self.frame_lock = threading.Lock()

        self.win = tkinter.Tk()
        self.win.configure(bg="lightgrey")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgrey")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, height = 10)
        self.text_area.config(font=('Arial', 12), state='disabled')
        self.text_area.pack(padx=20, pady=5)

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgrey")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.send_msg)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_active = True

    def receive_msg(self, message):
        with self.frame_lock:
            if self.gui_active:
                self.text_area.config(state='normal')
                self.text_area.insert('end', message)
                self.text_area.yview('end')
                self.text_area.config(state='disabled')

    def send_msg_wrapper(self, message):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.on_send(message))
        loop.close()

    def send_msg(self):
        message = self.input_area.get('1.0', 'end')
        threading.Thread(target=self.send_msg_wrapper, args=(message,)).start()
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.win.destroy()
