import socket
import threading
from cryptography.fernet import Fernet
import base64

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)

    def start(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print("Server started on {}:{}".format(self.host, self.port))
        except socket.error as e:
            print("Error starting the server:", e)
            return

        while True:
            try:
                client_socket, addr = server_socket.accept()
                self.clients.append(client_socket)
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            except socket.error as e:
                print("Error accepting client connection:", e)

    def handle_client(self, client_socket):
        try:
            encrypted_key = self.key
            client_socket.send(base64.urlsafe_b64encode(encrypted_key))
        except socket.error as e:
            print("Error sending encryption key to client:", e)
            self.remove_client(client_socket)
            return

        while True:
            try:
                encrypted_msg = client_socket.recv(1024)
                if not encrypted_msg:
                    self.remove_client(client_socket)
                    break

                decrypted_msg = self.fernet.decrypt(encrypted_msg).decode()
                print("Received message:", decrypted_msg)

                encrypted_reply = self.fernet.encrypt(decrypted_msg.encode())
                self.broadcast(encrypted_reply)
            except (socket.error, Fernet.InvalidToken) as e:
                print("Error handling client message:", e)
                self.remove_client(client_socket)
                break

    def broadcast(self, msg):
        for client in self.clients:
            try:
                client.send(msg)
            except socket.error as e:
                print("Error broadcasting message to a client:", e)
                self.remove_client(client)

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
            client_socket.close()

if __name__ == "__main__":
    server = ChatServer('0.0.0.0', 5000)
    server.start()
