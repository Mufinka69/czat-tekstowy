import threading
import socket
import json

import traceback

import logging
from logi_zajebane import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.running = True
        self.nickname = None
        self._file = None


    
    def send_json(self, response):
        response_json = (json.dumps(response) + "\n").encode('utf-8')
        logging.debug("send_json: %s", response_json)
        self.client.send(response_json)


    def receive_json(self):
        if self._file is None:
            self._file = self.client.makefile("r", encoding = 'utf-8')

        line = self._file.readline()
        if not line:
            return None

        msg = json.loads(line)
        logging.debug("receive_json: %s", msg)
        return msg


    # def receive_json2(self):
    #     data = self.client.recv(1024).decode('utf-8')
    #     print(f"Wiadomość -> {data}")
    #     data_json = json.loads(data)
    #     return data_json

    def set_nickname(self):
        nickname = None
        while self.running:
            try:
                data = self.receive_json()
                if data.get("type") == "request" and data.get("field") == "nickname":
                    nickname = input("Choose a nickname: ")
                    response = {"type": "nickname",
                                "nickname": nickname}
                    self.send_json(response)
                elif data.get("type") == "success" and data.get("field") == "nickname":
                    self.nickname = nickname
                    break
            except Exception as e:
                logger.exception("set_nickname")
                self.running = False
                break


    def receive(self):
        while self.running:
            try:
                data = self.receive_json()
                if data and data.get("type") == "message":
                    print(f'{data.get("nickname")}: {data.get("text")}')
            except Exception as e:
                # traceback.print_exc()
                logger.exception("receive error")
                self.running = False
                break
        logger.info("Server closed connection.")
        self.client.close()

    def write(self):
        while self.running:
            message = input()
            if message.strip() == "/exit":
                response = {"type": "command",
                            "command": "EXIT"}
                self.send_json(response)
                self.running = False
            elif message.strip() == "/users":
                response = {"type": "command",
                            "command": "USERS"}
                self.send_json(response)
            elif message != "":
                response = {"type": "message",
                            "nickname": self.nickname,
                            "text": message}
                self.send_json(response)
    

    def run(self):        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

        self.set_nickname()

        recive_thread = threading.Thread(target=self.receive)
        recive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()


client = Client("127.0.0.1", 9999)
client.run()