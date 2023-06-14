import socket
import threading
from cryptography.fernet import Fernet
import base64

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.key = None
        self.fernet = None

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.key_exchange()
        self.receive_messages()

    def key_exchange(self):
        encoded_key = self.client_socket.recv(1024)
        encrypted_key = base64.urlsafe_b64decode(encoded_key)
        self.key = Fernet(encrypted_key)

    def receive_messages(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        while True:
            message = input()
            encrypted_msg = self.key.encrypt(message.encode())
            self.client_socket.send(encrypted_msg)

    def receive(self):
        while True:
            encrypted_msg = self.client_socket.recv(1024)
            decrypted_msg = self.key.decrypt(encrypted_msg).decode()
            print("Received message:", decrypted_msg)

if __name__ == "__main__":
    client = ChatClient('192.168.8.231', 5000)
    client.connect()
