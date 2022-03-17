import socket
import tqdm
import os

HOST = "127.0.0.1"        # The remote host
PORT = 5555              # The same port as used by the server
BUFFER_SIZE = 4096

filename = "example.csv"
filesize = os.path.getsize(filename)

s = socket.socket()
print(f"[+] Connecting to {HOST}:{PORT}")
s.connect((HOST, PORT))
print("[+] Connected.")

progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
with open(filename, "rb") as f:
    while True:
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            break
        s.sendall(bytes_read)
        progress.update(len(bytes_read))
s.close()