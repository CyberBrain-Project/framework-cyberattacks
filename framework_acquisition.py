import socket

HOST = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 4096


def acquire_signals():
    print("[+] Acquiring signals...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with open("rawdata.csv", "wb") as f:
            print(f"Connected by {addr}")
            while True:
                bytes_read = conn.recv(BUFFER_SIZE)
                if not bytes_read:
                    print("Finished file transfer")
                    break
                f.write(bytes_read)
        f.close()
        conn.close()
        print("File transfer complete")


if __name__ == "__main__":
    acquire_signals()
