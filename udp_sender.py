import socket
import cv2,imutils,time
import base64
import struct

class sender():
    def __init__(self):
        self.BUFF_SIZE = 65536
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,self.BUFF_SIZE)
        host_name = socket.gethostname()
        self.host_ip = '0.0.0.0' #socket.gethostbyname(host_name)
        print(self.host_ip)
        self.port = 9999
        self.socket_address = (self.host_ip,self.port)
        self.server_socket.bind(self.socket_address)
        self.vid = ''
        self.payload_length = 96 - 6
        self.WIDTH = 400
        self.wait_send = 0 #wait receiver recovery data
        self.wait_cap = 0.01 #wait send deal the data

    def capture(self):
        self.vid = cv2.VideoCapture(r'/home/huaqing/Downloads/UDP TEST/4k.mp4')

    def work(self):
        fps,st,frames_to_count,cnt = (0,0,20,0)
        msg,client_addr = self.server_socket.recvfrom(self.BUFF_SIZE)
        print('GOT connection from ',client_addr,msg)
        while self.vid.isOpened():
            _,frame = self.vid.read()
            _,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,10])
            message = base64.b64encode(buffer)
            # print(message[:16],message[-16:])
            self.send_pkt(message,client_addr)
            frame = imutils.resize(frame,width = self.WIDTH)
            frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            cv2.imshow('TRANSMITTING VIDEO',frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.server_socket.close()
                break
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count/(time.time()-st))
                    st=time.time()
                    cnt=0
                except:
                    pass
            cnt+=1
            time.sleep(self.wait_cap)

    def send_pkt(self,data,address):
        message_len = len(data)
        if message_len > self.payload_length:
            for i in range(0,message_len//self.payload_length):
                temp_message = data[0:90]
                payload = struct.pack('!H',78) + struct.pack('!H',48) 
                payload = payload + struct.pack('!H',48)
                payload = payload + temp_message
                data = data[90:]
                self.server_socket.sendto(payload,address)
                time.sleep(self.wait_send)
            payload = self.pad(data)
            self.server_socket.sendto(payload,address)
            time.sleep(self.wait_send)
        else:
            payload = self.pad(data)
            self.server_socket.sendto(payload,address)
            time.sleep(self.wait_send)

    def pad(self,data):
        data_remains = len(data)
        pad_bits = int((self.payload_length - data_remains) / 2)
        payload = struct.pack('!H',89)
        payload = payload + struct.pack('!H',ord(str(data_remains//10)))
        data_remains = data_remains % 10
        payload = payload + struct.pack('!H',ord(str(data_remains)))
        payload = payload + data
        for j in range(0,pad_bits):
            payload = payload + struct.pack('!H',48)
        return payload


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                           MAIN
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////
def main():
    s= sender()
    s.capture()
    s.work()

if __name__ == '__main__':
    main()