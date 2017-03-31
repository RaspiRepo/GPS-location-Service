import io
import socket
import logging
import time
import threading
from queue import Queue
import os

[HOST, PORT] = "172.20.10.6", 9999

class log_debug(object):
    def __init__(self, fn_suffix=""):
        logfilename = time.strftime("%Y_%m_%d") + ".txt"
        self.logger = logging.getLogger('TensorFlow')
        hdlr = logging.FileHandler(logfilename, encoding='UTF8')
        formatter = logging.Formatter('%(asctime)s  %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def write_event(self, message):
        #log_time = "[" + time.strftime("%Y-%m-%d") + ' ' + time.strftime("%H:%M:%S") + "]"
        #self.logfile.write(log_time)
        #self.logfile.write(message + "\n")
        self.logger.info(message)

class gps_server(object):
    def __init__(self):
        self.thrd_state = 0
        self.latitude = 36.389444
        self.longitude = -123.081944
        self.log = log_debug("gps_log")
        return

    def setup_listen_server(self):
        self.thrd_state = 1
        # accept connections from outside
        self.serversocket.listen()
        while True and self.thrd_state == 1:
            self.clientsocket, self.address = self.serversocket.accept()
            print("new client connected " + self.address[0] + ":" + str(self.address[1]))

            #self.log.write_event("new client connected " + self.address[0] + ":" + str(self.address[1]))
            self.server_thrd = threading.Thread(target=self.get_message, args = (self.clientsocket, self.address)).start()
        return

    def stop(self):
        try:
            self.clientsocket.shutdown(0)
            #self.serversocket.shutdown(0)
            self.thrd_state = 0
        except:
            pass
        return
    def write_gps_log(self, lati, longt, cli_ip_addr):
        try:
            lat_long_str = self.current_location_gps_str()
            debug_log_str = cli_ip_addr[0] + ":" + str(cli_ip_addr[1]) + " " + " location " +  lat_long_str

            print('{}'.format(debug_log_str))

            self.log.write_event(debug_log_str)
        except OSError as err:
            self.log.write_event("write_gps_log error: {0}".format(err))

    def get_message(self, client_sock, client_address):
        try:
            while True and self.thrd_state == 1:

                # self.request is the TCP socket connected to the client
                self.data = client_sock.recv(512).strip()
                # print("{} wrote:".format(self.client_address[0]))
                try:
                    curr_gps_loc = self.data.decode('utf-8')
                    lat, lon = curr_gps_loc.split(',')
                    self.latitude = float(lat)
                    self.longitude = float(lon)

                    self.write_gps_log(self.latitude, self.longitude, client_address)

                    # just send back the same data, but upper-cased
                    client_sock.sendall(self.data.upper())
                except:
                    pass
                time.sleep(0.5)
                #self.log.write_event("gps service terminated")
        except OSError as err:
            self.log.write_event("OS error: {0}".format(err))
        return

    def setup_server(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((HOST, PORT))
        serv_thrd = threading.Thread(target=self.setup_listen_server).start()
        return

    def gps_to_dms(self, deg):
        d = int(deg)
        md = abs(deg - d) * 60
        m = int(md)
        sd = ((md - m) * 60)

        return [d, m, sd]

    def current_location(self):
        return [self.latitude, self.longitude]

    def current_location_gps_str(self):
        try:
            d, n, sd = self.gps_to_dms(self.latitude)
            hemi = 'N'
            if d < 0:
                hemi = 'S'

            d1, n1, sd1 = self.gps_to_dms(self.longitude)
            hemi1 = 'E'
            if d1 < 0:
                hemi1 = 'W'

            lat_long_str = '{}°'.format(abs(d)) + "{}`".format(n) + '{:2.1f}"'.format(sd) + ' {:2}'.format(hemi) + \
                           '{}°'.format(abs(d1)) + "{}`".format(n1) + '{:2.1f}"'.format(sd1) + ' {:1}'.format(hemi1)
        except OSError as err:
            self.log.write_event("current_location_gps_str error: {0}".format(err))

        return lat_long_str

if __name__ == '__main__':
    #setup and run gps location service
    gps_service = gps_server()
    gps_service.setup_server()