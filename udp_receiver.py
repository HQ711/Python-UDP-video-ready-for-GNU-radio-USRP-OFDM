import socket
import cv2,imutils,time
import base64
import numpy as np
import struct

class receiver():
    def __init__(self):
        self.BUFF_SIZE = 65536
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,self.BUFF_SIZE)
        host_name = socket.gethostname()
        self.host_ip = '0.0.0.0' #socket.gethostbyname(host_name)
        print(self.host_ip)
        self.port = 9999
        self.socket_address = (self.host_ip,self.port)
        self.udp_message = b'Hello'

    def work(self):
        fps,st,frames_to_count,cnt = (0,0,20,0)
        flag = False
        message = b''
        WIDTH = 400
        while True:
            packet,_ = self.client_socket.recvfrom(self.BUFF_SIZE)
            message, flag = self.recover_data(message,packet)
            if flag:
                try:
                    data = base64.b64decode(message,' /')
                    npdata = np.frombuffer(data,dtype=np.uint8)
                    frame = cv2.imdecode(npdata,1)
                    frame = imutils.resize(frame,width = WIDTH)
                    frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                    cv2.imshow("RECEIVING VIDEO",frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        self.client_socket.close()
                        break
                    if cnt == frames_to_count:
                        try:
                            fps = round(frames_to_count/(time.time()-st))
                            st=time.time()
                            cnt=0
                        except:
                            pass
                    cnt+=1
                except:
                    pass
                flag = False
                message = b''

    def recover_data(self,message,data):
        if struct.unpack('!H',data[0:2])==(78,):
            message = message + data[6:]
            flag = False
        elif struct.unpack('!H',data[0:2])==(89,):
            index = 0
            ten_digit = struct.unpack('!H',data[2:4])
            one_digit = struct.unpack('!H',data[4:6])
            index = 10 * int(chr(ten_digit[0])) + \
                    1 * int(chr(one_digit[0]))	
            if index == 0:
                flag = True
                # sys.stderr.write('-')
            else:
                message = message + data[6:(index+6)]
                flag = True
        return message,flag



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                           MAIN
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////
def main():
    r = receiver()
    r.client_socket.sendto(r.udp_message,r.socket_address)
    r.work()

if __name__ == '__main__':
    main()