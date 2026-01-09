import threading
import socket
import json

import traceback

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.nickname = input("Choose a nickname: ")
        self.running = True


    
    def send_json(self, response):
        response_json = json.dumps(response).encode('utf-8')
        self.client.send(response_json)


    def recieve_json(self):
        data = self.client.recv(1024).decode('utf-8')
        data_json = json.loads(data)
        return data_json

    def receive(self):
        while self.running:
            try:
                data = self.recieve_json()
                # print(f"Otrzymano: {data}")
                if data.get("field") == "nickname":
                    response = {"type": "nickname",
                                "nickname": self.nickname}
                    # print(f"Wysłano: {response}")
                    self.send_json(response)
                elif data.get("type") == "message":
                    print(f'{data.get("nickname")}: {data.get("text")}')
            except Exception as e:
                print(e)
                traceback.print_exc()
                self.running = False
                break
        print("Server closed connection.")
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
            else:
                response = {"type": "message",
                            "nickname": self.nickname,
                            "text": message}
                # print(response)
                self.send_json(response)
    

    def run(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

        recive_thread = threading.Thread(target=self.receive)
        recive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()


client = Client("127.0.0.1", 9999)
client.run()