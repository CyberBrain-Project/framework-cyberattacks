import socket
import tqdm
import os




HOST = "127.0.0.1"        # The remote host
PORT = 5555              # The same port as used by the server
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST, PORT))
#f = open('example.csv')
#print ("Sending Data ....")
#while True:
#    for line in f:
#        print(line)
#        s.send(line)
#    break
#f.close()
#print ("Sending Complete")
#s.close()

# the name of file we want to send, make sure it exists
filename = "example.csv"
# get the file size
filesize = os.path.getsize(filename)


s = socket.socket()
print(f"[+] Connecting to {HOST}:{PORT}")
s.connect((HOST, PORT))
print("[+] Connected.")
# start sending the file
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