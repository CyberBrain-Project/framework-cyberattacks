import socket

HOST = ""
PORT = 5555
BUFFER_SIZE = 4096

print("Starting acquisition module...")
print("Server running", HOST, PORT)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with open("rawdata.csv", "wb") as f:
        print(f"Connected by {addr}")
        while True:
            bytes_read = conn.recv(BUFFER_SIZE)
            if not bytes_read:
                print("No data received")
                break
            f.write(bytes_read)
    f.close()
    conn.close()
s.close()