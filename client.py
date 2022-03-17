import socket

HOST = '127.0.0.1'        # The remote host
PORT = 5555              # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
f = open('prueba.csv', 'rb')
print ("Sending Data ....")
l = f.read()
while True:
    for line in l:
        s.send(line)
    break
f.close()
print ("Sending Complete")
s.close()