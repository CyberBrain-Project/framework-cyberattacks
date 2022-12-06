from scapy.all import *
import csv
from datetime import datetime
import sys
from io import StringIO

if __name__ == "__main__":

    '''
        Creation of the CSV file that will contain the number of each packet type obtained for each instant.
    '''
    filename='detection_attacks.csv'
    with open(filename, 'w', encoding='UTF8') as f:
        file_writer = csv.writer(f)
        header = ['timestamp', 'Raw', 'Disconnect_Req', 'Disconnect_Resp', 'Connect_Req', 'Connect_Resp', 'Echo_req', 'Echo_resp', 'Type']
        file_writer.writerow(header)
        f.close()

    '''
        Duration of time that the detection script will be running.
    '''
    delay = 60*240 
    close_time = time.time() + delay

    '''
        Obtaining the type to be added in each row of the CSV file.
    '''
    if sys.argv[1] == '1':
        option = 'normal_use'
    elif sys.argv[1] == '2':
        option = 'battery_draining'
    elif sys.argv[1] == '3':
        option = 'dos'
    else:
        option = ''

    if option != '':
        while(True):
            '''
                If time has passed the program closes.
            '''
            if time.time() > close_time:
                break
        
            n_raw = 0
            n_disconn_req = 0
            n_disconn_resp = 0
            n_conn_req = 0
            n_conn_resp = 0
            n_echo_req = 0
            n_echo_resp = 0

            '''
                Creating a BluetoothHCISocket to sniff the Bluetooth interface.
            '''
            bt = BluetoothHCISocket(0) 

            '''
                Packets are obtained for five seconds.
            '''
            pkts = bt.sniff(timeout=5)

            '''
                For each package, its type is obtained, and the number of packages obtained corresponding to its type is increased.
            '''
            for pkt in pkts:
                '''
                    Redirection the output of the packet.show() to the variable 'capture' to detect echo_req and echo_res packages.
                '''
                capture = StringIO()
                save_stdout = sys.stdout
                sys.stdout = capture
                pkt.show()
                sys.stdout = save_stdout

                '''
                    The package type is saved. To do this, the output of the package.summary() is saved in the variable 'capture2', 
                    and the rsplit function obtains its type.
                '''
                capture2 = StringIO()
                print(pkt.summary().rsplit('/', 1)[-1], file=capture2)
                type_packet = capture2.getvalue()
                type_packet = type_packet.rsplit(' ', 1)[-1].strip()

                '''
                    Increment of counter associated with each package type.
                '''
                if (type_packet == "Raw") and ("echo_req" not in capture.getvalue()) and ("echo_res" not in capture.getvalue()):
                    n_raw += 1
                elif type_packet == "L2CAP_DisconnReq":
                    n_disconn_req += 1
                elif type_packet == "L2CAP_DisconnResp":
                    n_disconn_resp += 1
                elif type_packet == "L2CAP_ConnReq":
                    n_conn_req += 1
                elif type_packet == "L2CAP_ConnResp":
                    n_conn_resp += 1
                elif "echo_req" in capture.getvalue():
                    n_echo_req += 1
                elif "echo_res" in capture.getvalue():
                    n_echo_resp += 1
            
            '''
                The number of each packet type is added to the CSV file indicating the current instant.
            '''
            row = [datetime.now(), n_raw, n_disconn_req, n_disconn_resp, n_conn_req, n_conn_resp, n_echo_req, n_echo_resp, option]
            with open(filename, 'a', encoding='UTF8') as f:
                file_writer = csv.writer(f)
                file_writer.writerow(row)
                f.close()

    '''
        If option is not in [1, 2, 3], print the usage of this script.
    '''
    else:
        print("Usage: " + sys.argv[0] + " <option>, where:")
        print("option is 1 if you can obtain packets from a normal use.")
        print("option is 2 if you can obtain packets from a battery-draining attack.")
        print("option is 3 if you can obtain packets from a dos attack.")
