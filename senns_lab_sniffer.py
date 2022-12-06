import argparse
from scapy.all import *
import socket
import zipfile
from os import remove

class Sniffer:
    '''
        This class contains all the methods used to capture the packages in the indicated interface, generate de .pcap file, zip it
        and send through a tcp socket to the specified IP and port.
    '''

    def __init__(self, args, capture=[], zip="", pcap_file=""):
        self.args = args

    def __call__(self, packet):
        if self.args.verbose:
            packet.show()
        else:
            print(packet.summary())

    def sniff_packets(self):
        '''
            Method used for sniffing the traffic in the interface passed as a parameter. It is possible to indicate the desired 
            number of packets to sniff with the parameter 'count'. It is also possible to apply a filter to sniff only the indicated
            packets.
        '''
        self.capture = sniff(iface=self.args.interface, prn=self, store=1, count=100, filter="tcp")

    def generate_pcap(self):
        '''
            Generates the .pcap file with the packets captured.
        '''
        now = datetime.now()
        self.pcap_file = "capture-{}.pcap".format(now.strftime("%d-%m-%Y-%H-%M-%S"))
        wrpcap(self.pcap_file, self.capture)
        self.capture = []

    def zip_file(self):
        '''
            Compresses the .pcap file into a .zip file.
        '''
        now = datetime.now()
        self.zip = "capture-{}.zip".format(now.strftime("%d-%m-%Y-%H-%M-%S"))
        zip_file = zipfile.ZipFile(self.zip, 'w')
        zip_file.write(self.pcap_file)
        zip_file.close()

    def send_capture(self):
        '''
            Opens a socket and sends the compressed capture to the specified IP address and port.
        '''

        self.zip_file()
        
        host = self.args.dest
        port = self.args.port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host,port))

            with open(self.zip, "rb") as f:

                while True:
                    bytes_read = f.read(4096)
                    if not bytes_read:
                        break
                    s.sendall(bytes_read)

        s.close()

        remove(self.pcap_file)
        remove(self.zip)





if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='be more talkative')
    parser.add_argument('-i', '--interface', type=str, required=True, help='network interface name')
    parser.add_argument('-d', '--dest', type=str, required=True, help="Destination IP")
    parser.add_argument('-p', '--port', required=True, help="Destination port")
    args = parser.parse_args()
    sniffer = Sniffer(args)

    try:
        while True:
            sniffer.sniff_packets()
            sniffer.generate_pcap()
            sniffer.send_capture()
    except KeyboardInterrupt:
        print('Capture finished')
    



