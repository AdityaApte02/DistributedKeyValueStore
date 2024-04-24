from replica import Replica
import socket
import threading
import time
from message import SetMessage, GetMessage
import os
import random
import datetime

class Client():
    def __init__(self,client_id, replicas,requests, congifObj, output_path):
        self.clock = random.randint(1, 50)
        self.client_id = client_id
        self.replicas = replicas
        self.requests = requests
        self.host = congifObj["Clienthost"]
        self.port = congifObj["Clientport"]
        self.output_path = output_path
        print(f'Client {self.client_id} started')
        self.run()
        
    def __str__(self) -> str:
        return f'Client {self.client_id} started and is listening on {self.host}:{self.port}'
        
    def send(self,host,port,message):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.sendall(bytes(message, "utf-8"))
            sock.close()
            return True
        except Exception as E:
            return False
        
    def setRequest(self,key,value, replica_id):
        cur_time = datetime.datetime.now().timestamp() * 1000
        msg = SetMessage(self.clock, cur_time, self.host, self.port, key, value, replica_id, True).serialize()
        self.send(self.replicas[replica_id-1]["replicaHost"],self.replicas[replica_id-1]["replicaPort"],msg)
    
    def getRequest(self,key, replica_id):
        cur_time = datetime.datetime.now().timestamp() * 1000
        msg = GetMessage(self.clock, cur_time, self.host, self.port, key, replica_id).serialize()
        self.send(self.replicas[replica_id-1]["replicaHost"],self.replicas[replica_id-1]["replicaPort"],msg)
    
        
    def handleReponse(self,response):
        with open(self.output_path, "a") as file:
            file.write(response + "\n")
        
        
        
    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host,self.port))
        sock.listen(10)
        print(f"Client {self.client_id} is listening on {self.host}:{self.port}")
        while True:
            sck,addr = sock.accept()
            data = sck.recv(1024)
            print(f"Client {self.client_id} received data: {data.decode('utf-8')}")
            self.handleReponse(data.decode("utf-8"))
        
    def sendRequest(self,request):
        for request in self.requests:
            self.clock = self.clock + random.randint(1,10)
            if request["type"] == "set":
                self.setRequest(request["key"],request["value"],request["replica"])
            elif request["type"] == "get":
                self.getRequest(request["key"],request["replica"])
            time.sleep(0.1)
            
            
    def clearBuffers(self):
        with open(self.output_path, "w") as file:
            pass
        
    def run(self):
        self.clearBuffers()
        listenThread = threading.Thread(target=self.listen).start()
        self.sendRequest(self.requests)
        