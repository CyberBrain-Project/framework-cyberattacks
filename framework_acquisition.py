import socket

HOST = "0.0.0.0"
PORT = 5555
BUFFER_SIZE = 4096

print("Server running", HOST, PORT)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with open("rawdata.csv", "wb") as f:
        print(f"Connected by {addr}")
        while True:
            print("1")
            bytes_read = s.recv(BUFFER_SIZE)
            #data = "".join(iter(lambda: conn.recv(1), "\n"))
            print("2")
            if not bytes_read:
                print("No data")
                break
            else:
                print(bytes_read)
            #if not data:
            #    break
            f.write(bytes_read)
    f.close()
    conn.close()