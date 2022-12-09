import psutil
from scapy.all import *
from datetime import datetime
import csv
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


class Monitor:
    '''
        This class contains all the methods used to gather all the statistics the selected statistics for the detection of the man-in-the-middle attack.
        It allows measurements of network usage to be obtained by capturing traffic, as well as measurements to determine computer workload.
    '''


    def __init__(self):
        self.pkt_sizes = []
        self.n_tcp = 0
        self.n_udp = 0
        self.n_icmp = 0
        self.n_other = 0
        self.capturedPacketsSize = 0
        self.last_bytes_sent = 0
        self.last_bytes_rcv = 0
        self.clf = joblib.load('man-in-the-middle-detection.pkl')

    def get_stats(self, file_writer):
        '''
            Creates an sniffer that captures the traffic asynchronously while other computer metrics are obtained. Specifically it measures the CPU %, 
            CPU frequency, RAM usage, RAM %, Swap usage, Total Swap, Swap %, number of PIDs, number of opened sockets and output/input bytes.
        '''
        self.capturedPacketsSize = 0
        self.n_tcp = 0
        self.n_udp = 0
        self.n_icmp = 0
        self.n_other = 0

        sniffer = AsyncSniffer(iface='Wi-Fi',prn=self.packet_stats)
        sniffer.start()

        cpu_usage = psutil.cpu_percent(10) #%

        cpu_frequency = psutil.cpu_freq().current #MHz
     
        ram_usage = self.get_ram_usage()   #MB
    
        ram_pct = self.get_ram_usage_pct() #%
     
        swap_usage = self.get_swap_usage() #MB
   
        swap_total = self.get_total_swap() #MB
 
        swap_pct = psutil.swap_memory().percent
        pids = len(psutil.pids())
        n_sockets = len(psutil.net_connections())
        bytes_io = self.net_usage()

        print('CPU_pct:',cpu_usage,'Frequency:',cpu_frequency,'RAM Usage:',ram_usage,'RAM_pct:', ram_pct,'Swap Usage:',swap_usage,'Total Swap:',swap_total,'Swap_pct:', swap_pct,'PIDS',pids,
            'NSockets:',n_sockets,"TCP:",self.n_tcp,"UDP:",self.n_udp,"ICMP:",self.n_icmp,"Other:",self.n_other,"Total bytes:",self.capturedPacketsSize,"Bytes-Rcv",bytes_io[0], 'Bytes-Sent', bytes_io[1])

        sniffer.stop()

        row = [ cpu_usage, 
                cpu_frequency, 
                ram_usage, 
                ram_pct, 
                swap_usage,
                swap_pct,  
                swap_total, 
                pids,
                n_sockets, 
                self.n_tcp, 
                self.n_udp, 
                self.n_icmp,
                self.n_other, 
                self.capturedPacketsSize,
                bytes_io[0],
                bytes_io[1], 
                datetime.now()]

        self.check_attack(row)
        file_writer.writerow(row)

        

    def packet_stats(self, packet):
        '''
            Used as a callback function for the Sniffer. It checks the protocol of the packet being passed as a parameter and increments the counter associated 
            with that packet type.
        '''
        self.capturedPacketsSize += len(packet)

        if(packet.haslayer(scapy.layers.inet.UDP)):
            self.n_udp = self.n_udp+1
        elif(packet.haslayer(scapy.layers.inet.TCP)):
            self.n_tcp = self.n_tcp+1
        elif(packet.haslayer(scapy.layers.inet.ICMP)):
            self.n_icmp = self.n_icmp+1
        else:
            self.n_other = self.n_other+1

    def get_ram_usage(self):
        '''
            Returns the RAM usage in MB.
        '''
        return int(psutil.virtual_memory().total - psutil.virtual_memory().available)/1024/1024

    def get_ram_usage_pct(self):
        '''
            Returns the RAM usage in percentage.
        '''
        return psutil.virtual_memory().percent

    def get_swap_usage(self):
        '''
            Returns the Swap usage in MB.
        '''
        return int(psutil.swap_memory().used)/1024/1024

    def get_total_swap(self):
        '''
            Returns the total Swap in MB.
        '''
        return int(psutil.swap_memory().total/1024/1024)

    def net_usage(self, interface='Wi-Fi'):
        '''
            Return a tuple of bytes sent and received over the interface.
        '''

        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[interface]
        rcv = net_stat.bytes_recv
        sent = net_stat.bytes_sent

        net_in = round((rcv - self.last_bytes_rcv), 3)
        net_out = round((sent - self.last_bytes_sent), 3)

        self.last_bytes_rcv = rcv
        self.last_bytes_sent = sent

        return [net_in, net_out]

    def check_attack(self, row):
        '''
            Gets the row with the statistics monitored and return the prediction of the trained model to determine
            if there is a attack.
        '''

        header = ['CPU-pct','Frequency','RAM Usage','RAM-pct','Swap Usage','Swap-pct','Total Swap','PIDS','NSockets','TCP', 'UDP','ICMP', 'Other', 'Total Bytes', 'Bytes-Rcv', 'Bytes-Sent']
        row = row[:16]

        row_test = pd.DataFrame([row], columns=header)
        print(self.clf.predict(row_test)[0])

        if(self.clf.predict(row_test)[0]):
            print('** WARNING: Possible man-in-the-middle attack detected **')
            print('Highly recommended to stop the experiment, data leakage could occur.')
        else:
            print('** No attack detected **')
        print()

        


def main():

    now = datetime.now()
    filename = "usage-stats-{}.csv".format(now.strftime("%d-%m-%Y-%H-%M-%S"))

    file = open(filename, 'w', newline = '')
    file_writer = csv.writer(file)


    header = ['CPU-pct','Frequency','RAM Usage','RAM-pct','Swap Usage','Swap-pct','Total Swap','PIDS','NSockets','TCP', 'UDP','ICMP', 'Other', 'Total Bytes', 'Bytes-Rcv', 'Bytes-Sent','Timestamp']
    file_writer.writerow(header)

    monitor = Monitor()

    try:
        while True:
            monitor.get_stats(file_writer)

    except: KeyboardInterrupt


if __name__ == '__main__':
    main()