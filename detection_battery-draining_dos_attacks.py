from scapy.all import *
import csv
from datetime import datetime
import sys
from io import StringIO
import joblib
import pandas as pd
import random

if __name__ == "__main__":

    '''
        Pkl file containing the trained classification model.
    ''' 
    clf = joblib.load('detection_attacks.pkl')

    header = ['Raw', 'Disconnect_Req', 'Disconnect_Resp', 'Connect_Req', 'Connect_Resp', 'Echo_req', 'Echo_resp']

    '''
        Duration of time that the detection script will be running.
    '''
    delay = 60*240 
    close_time = time.time() + delay

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
            Gets the row with the number of each package type monitored and return the prediction of the trained model to determine 
            if there is no attack or what type of attack is occurring.
        '''
        
        row = [n_raw, n_disconn_req, n_disconn_resp, n_conn_req, n_conn_resp, n_echo_req, n_echo_resp]

        print('Raw:',n_raw,'Disconn_req:',n_disconn_req,'Disconn_resp:',n_disconn_resp,'Conn_req:',n_conn_req,'Conn_resp:',n_conn_resp,'Echo_req:',n_echo_req,'Echo_res:',n_echo_resp)

        row_test = pd.DataFrame([row], columns=header)

        if(clf.predict(row_test)[0] == 'normal_use'):
            print('** All values analyzed. No anomaly detected. **')
        elif(clf.predict(row_test)[0] == 'battery_draining'):
            print('** WARNING: Possible battery-draining attack detected. **')
        else:
            print('** WARNING: Possible Denial of Service attack detected. **')

        print()