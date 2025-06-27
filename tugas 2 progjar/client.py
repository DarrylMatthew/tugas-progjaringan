import socket

def main():
    host = '127.0.0.1'
    port = 45000

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print(f"Koneksi gagal. Pastikan server ({host}:{port}) sudah berjalan.")
        return

    while True:
        command = input("Enter a command (TIME/QUIT): ").strip().upper()

        if not command:
            continue

        client_socket.sendall(f"{command}\r\n".encode('utf-8'))

        if command != "QUIT":
            try:
                response = client_socket.recv(1024).decode('utf-8').strip()
                if response:
                    print(f"Server response: {response}")
                else:
                    print("Koneksi ditutup oleh server.")
                    break
            except Exception as e:
                print(f"Gagal menerima data: {e}")
                break
        else:
            break

    client_socket.close()
    print("Koneksi dengan server ditutup.")

if __name__ == "__main__":
    main()