
import socket
import threading
import time


class Server:
    Clients = []
    # 建立一个消息字典
    client_msg={}
    def __init__(self,host,port):
        self.host = host
        self.port = port

        self.network = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.network.bind((self.host,self.port))
        self.network.listen(20)

        print(f'server listen at {self.port}')
        threading.Thread(target=self.pinger).start()


    # 心跳线程
    def pinger(self):
        while True:
            time.sleep(1)
            for client in Server.Clients:
                try:
                    msg = 'ß'.encode('ISO-8859-1')
                    # print('ß')
                    client.sock.send(msg)
                except ConnectionResetError:
                    print('ConnectionResetError')
                    client.terminate()
                    Server.Clients.remove(client)
                    pass
                except ConnectionAbortedError:
                    client.terminate()
                    Server.Clients.remove(client)
                    print('ConnectionAbortedError')
                    pass
    # 监听
    def start(self):
        while True:
            client_sock, client_addr = self.network.accept()
            print(f'client {client_addr} connected')

            client_sock.send('HLO'.encode())
            time.sleep(0.1)

            msg = ' '
            for client in Server.Clients:
                msg = msg + ' ' + client.clientID
            # msg = '  zhangsan lisi'
            client_sock.send(msg.encode('utf-8'))
            client_thread = threading.Thread(target=self.wait_for_user_nickname,args=[client_sock])
            client_thread.start()
    # 接收一个用户
    def wait_for_user_nickname(self, client_sock):
        new_user_id = client_sock.recv(1024).decode('utf-8')
        print(new_user_id)
        # 获取sock对象，userid（昵称）
        client = Client(client_sock,new_user_id)

        # 发送之前的canvas
        for client_ID in Server.client_msg:
            client_msg=Server.client_msg[client_ID]
            client_msg=client_msg.encode('ISO-8859-1')
            client_sock.sendall(client_msg)

        Server.Clients.append(client)
        client.start()
        Server.client_msg[client_ID]+=client.msg
        print(Server.client_msg)


class Client:
    def __init__(self, sock, clientID):
        self.sock = sock
        self.clientID = clientID
        self._run = True
        Server.client_msg[self.clientID]=''
    def terminate(self):
        self._run = False

    def start(self):
        while self._run:
            msg = ''
            while True:
                # 收消息，1个字节1个字节收
                data = self.sock.recv(1).decode('ISO-8859-1')
                msg += data
                if data == 'Ø':
                    break
            # print(msg)
            if msg[0] == 'D':
                self.broadcast2Clients(msg)

            pass

    def broadcast2Clients(self,msg):
        Server.client_msg[self.clientID] += msg
        msg = msg.encode('ISO-8859-1')

        for client in Server.Clients:
            client.sock.sendall(msg)


if __name__ == '__main__':
    server = Server('0.0.0.0',6000)
    server.start()
