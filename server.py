import threading
import socket
import os
import json
from enum import Enum




class Commands(Enum):
    EXIT = "EXIT"
    USERS = "USERS"
    BROADCAST = "/broadcast"
    KICK = "/kick"
    CLS = "CLS"
    MESSAGE = "message"

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
        self.server = None

    def broadcast(self, message, user1):
        message_json = json.dumps(message).encode('utf-8')
        for user in self.users:
            if user != user1:
                user.client.send(message_json)

    def handle_user(self, user):
        while not self.kill:
            try:
                data_b = user.client.recv(1024)
                if not data_b:
                    raise Exception("Disconnected")
                
                data = data_b.decode('utf-8')
                data_json = json.loads(data)


                if data_json["type"] == "command":
                    command = Commands(data_json["command"])

                    if command == Commands.USERS:
                        users_list  = [u.nickname for u in self.users]
                        response = {"type": "system",
                                    "command": "USERS",
                                    "users": users_list
                        }
                        user.client.send(json.dumps(response).encode("utf-8"))

                    elif command == Commands.EXIT:
                        response = {"type": "system",
                                    "command": "EXIT",
                                    "text": f"{user.nickname} left the chat"
                        }
                        self.broadcast(response, None)
                        print(f"{user.nickname} left the chat")
                        raise Exception("User exited")
                    
                elif data_json["type"] == "message":
                    response = {"type": "message",
                                "nickname":user.nickname,
                                "text": data_json["text"]
                                }
                    self.broadcast(response, user)
                    
            except:
                if user in self.users:
                    self.users.remove(user)
                    response = {"type": "system",
                                "text": f"{user.nickname} left the chat"
                    }
                    self.broadcast(response, user)                    
                    user.client.close()
                break
                    

    def is_valid_nickname(self, client):
        request  = {"type": "request",
                    "field": "nickname"}
        client.send(json.dumps(request).encode('utf-8'))
        # print(f"Wysłano {request}")
        # while True:
        data_b = client.recv(1024)
        data_json = json.loads(data_b.decode('utf-8'))
        # print(f"Otrzymano: {data_json}")

        nickname = data_json.get("nickname", "").strip()
        # print(nickname)
            # break

            # if not (1 <= len(nickname) <= 15):
            #     request  = {"type": "request",
            #                 "field": "nickname"}
            #     client.send(json.dumps(request).encode('utf-8'))
            # elif any(u.nickname == nickname for u in self.users):
            #     request  = {"type": "request",
            #                 "field": "nickname"}
            #     client.send(json.dumps(request).encode('utf-8'))
            # if any(c in " !@#$%^&*()" for c in nickname):
            #     request  = {"type": "request",
            #                 "field": "nickname"}
            #     client.send(json.dumps(request).encode('utf-8'))
            # else:
                # request = {"type": "success",
                #             "field": "nickname",
                #            "text": "Nickname accepted."}
                # client.send(json.dumps(request).encode('utf-8'))
                # break
        return nickname

    def accept_connections(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        print("Server started ...")

        while not self.kill:
            try:
                client, addr = self.server.accept()
            except OSError:
                break

            print(f"Coneccted with {str(addr)}")

            nickname = self.is_valid_nickname(client)
            user = User(client, nickname)
            self.users.append(user)
            print("Users:", ", ".join(a.nickname for a in self.users))
            response = {"type":"system",
                        "command": "CONNECTED",
                        "text": "Coneccted to the server"
            }
            print(f"Wysłano: {response}")
            print("")
            client.send(json.dumps(response).encode('utf-8'))
            response = {"type":"system",
                        "command": "JOIN",
                        "nickname": nickname,
                        "text": f"{nickname} join the chat"
            }
            print(f"Wysłano: {response}")
            print("")
            client.send(json.dumps(response).encode('utf-8'))
            print(f"Nickname of the client is {nickname}!")
            print("")
            thread = threading.Thread(target=self.handle_user, args=(user, ), daemon=True)
            thread.start()


    # def kick_user(self, cmd):
    #     nick = cmd.split(" ", 1)[1]
    #     for u in self.users:
    #         if u.nick == nick:                        
    #             u.client.send("You were kicked".encode('utf-8'))
    #             u.client.close()
    #             self.users.remove(u)
    #             self.broadcast(f"{nick} was kicked", None)
    #             break


    # def close_server(self):
    #     print("self.kill = true")
    #     self.kill = True
    #     self.server.close()

    # def send_message(self, cmd):
    #     message = cmd.split(" ", 1)[1]
    #     self.broadcast(message, None)

    # def clean_command_line(self):
    #     os.system("cls" if os.name == "nt" else "clear")
    
    # def print_users(self):
    #     print(f"Users: ", ", ".join(u.nickname for u in self.users))


    # def cmd(self):
    #     while not self.kill:
    #         cmd = input("")
    #         if cmd == "/exit":
    #             self.close_server()

    #         elif cmd == "/users":
    #             self.print_users()

    #         elif cmd == "/cls":
    #             self.clean_command_line(cmd)

    #         elif cmd.startswith("/broadcast "):
    #             self.send_message(cmd)

    #         elif cmd.startswith("/kick "):
    #             self.kick_user(cmd)



    def run(self):
        # threading.Thread(target=self.cmd, daemon=True).start()
        self.accept_connections()


Server("127.0.0.1", 9999).run()
