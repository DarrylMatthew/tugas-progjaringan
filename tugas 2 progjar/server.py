import socket
import threading
import logging
from datetime import datetime
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s')

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                data = self.connection.recv(32)
                if data:
                    command = data.decode('utf-8').strip()
                
                    if command == "TIME":
                        now = datetime.now()
                        current_time = now.strftime("%H:%M:%S")
                        response = f"JAM {current_time}\r\n"
                        self.connection.sendall(response.encode('utf-8'))

                    elif command == "QUIT":
                        break
                else:
                    break
            except Exception as e:
                logging.error(f"Error handling client {self.address}: {e}")
                break

        logging.info(f"Koneksi dengan {self.address} ditutup.")
        self.connection.close()

class Server(threading.Thread):
    def __init__(self, port):
        self.the_clients = []
        self.port = port
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', self.port))
        self.my_socket.listen(1)
        logging.info(f"Server berjalan di port {self.port}")
        
        while True:
            connection, client_address = self.my_socket.accept()
            logging.info(f"Koneksi diterima dari {client_address}")

            clt = ProcessTheClient(connection, client_address)
            clt.start()
            self.the_clients.append(clt)

def main():
    svr = Server(45000)
    svr.start()

if __name__ == "__main__":
    main()