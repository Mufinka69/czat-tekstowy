import threading
import socket


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.nickname = input("Choose a nickname: ")
        self.running = True

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('ascii')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('ascii'))
                else:
                    print(message)
            except:
                print("error")
                self.running = False
                break
        self.client.close()

    def write(self):
        while self.running:
            message = input(f"{self.nickname}: ")
            if message.strip() == "/exit":
                self.client.send("/exit".encode("ascii"))
                self.running = False
            else:
                self.client.send(message.encode('ascii'))
    

    def run(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

        recive_thread = threading.Thread(target=self.receive)
        recive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()


client = Client("127.0.0.1", 9999)
client.run()