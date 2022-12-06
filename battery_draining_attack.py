from bbt import *
import time
import csv
from datetime import datetime

if __name__ == "__main__":
    import sys

    '''
        Function that performs ten attempts to connect or disconnect to the device.
    '''
    def try_to(condition, action, tries, message=None):
        t = 0
        while (not condition() and t < tries):
            t += 1
            if message:
                print("{} ({}/{})".format(message, t, tries))
            action()
        return condition()

    if (len(sys.argv) > 1): 

        '''
            Creation of the CSV file that will contain the battery level obtained for each instant.
        '''
        now = datetime.now()
        filename = "battery-draining-log-{}.csv".format(now.strftime("%d-%m-%Y-%H-%M-%S"))
        with open(filename, 'a', encoding='UTF8') as f:
            file_writer = csv.writer(f)
            header = ['timestamp', 'battery']
            file_writer.writerow(header)
            f.close()
        
        name = sys.argv[1]    
        i = 0

        while True:
            
            with Device(name) as device:
                '''
                    Call to the try_to function for connection to the device.
                '''
                if not try_to(device.is_connected, device.connect, 10, "Connecting to {}".format(name)):
                    print("unable to connect")

                print ("Connected")

                '''
                    Device synchronization.
                '''
                sync = device.synchronize()
                print ("Synchronization: ", sync)

                ''' 
                    Variable i sets the number of connections and disconnections before obtaining the battery.
                '''
                if i == 50:
                    device.start()

                    '''
                        In the first 30 messages, the battery is not available and in the message arrives a -1. 
                        Messages are received from the controller until the battery is != 1.
                    '''
                    bat = False

                    while bat == False:
                        '''
                            Messages sent by the controller are read.
                        '''
                        sequence, battery, flags, data = device.read()

                        if battery != -1:
                            print('--------------------------------------')
                            print('Battery: ',battery, " ", "Seq :",sequence)
                            print('--------------------------------------')

                            '''
                                The battery level is added to the CSV file indicating the current instant.
                            '''
                            current_time = datetime.now()
                            row = [current_time, battery]
                            with open(filename, 'a', encoding='UTF8') as f:
                                file_writer = csv.writer(f)
                                file_writer.writerow(row)
                                f.close()

                            bat = True
                            i = -1

                '''
                    If the device is connected, ten disconnect attempts are made.
                '''
                if device.is_connected(): 
                    if not try_to(lambda: not device.is_connected(), device.disconnect, 10):
                        print("unable to disconnect")  
                print("Disconnected")
                
                i = i + 1

                '''
                    Sleep between connections.
                ''' 
                time.sleep(0.1)
  
    else:
        print("Usage: " + sys.argv[0] + " <device name>")