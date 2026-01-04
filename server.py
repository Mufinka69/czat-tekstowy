import threading
import socket


class User:
    def __init__(self, client, nickname):
        self.client = client #socket
        self.nickname = nickname


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.users = []
        self.kill = False

    def broadcast(self, message, user1):
        for user in self.users:
            if user != user1:
                user.client.send(message)

    def handle_user(self, user):
        while not self.kill:
            try:
                message_b = user.client.recv(1024)
                if not message_b:
                    raise Exception("Disconnected")
                
                message = message_b.decode('ascii')

                if message == '/users':
                    users_list  = ", ".join([u.nickname for u in self.users])
                    user.client.send(f"users: {users_list}".encode('ascii'))
                elif message == '/exit':
                    self.broadcast(f"{user.nickname} left the chat".encode('ascii'))
                    print(f"{user.nickname} left the chat")
                    raise Exception("User exited")
                else:
                    self.broadcast(f"{user.nickname}: {message}".encode('ascii'), user)

            except:
                if user in self.users:
                    self.users.remove(user)
                    self.broadcast(f"{user.nickname} left the chat".encode('ascii'), user)                    
                    user.client.close()
                break
                    

    def accept_connections(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print("Server started ...")

        while not self.kill:
            client, addr = server.accept()
            print(f"Coneccted with {str(addr)}")

            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii') 

            user = User(client, nickname)
            self.users.append(user)
            client.send('Coneccted to the server'.encode('ascii'))
            
            self.broadcast(f"{nickname} join the chat".encode('ascii'), user)
            print(f"Nickname of the client is {nickname}!")


            thread = threading.Thread(target=self.handle_user, args=(user, ), daemon=True)
            thread.start()

    def cmd(self):
        while True:
            pass


    def run(self):
        self.accept_connections()


Server("127.0.0.1", 9999).run()