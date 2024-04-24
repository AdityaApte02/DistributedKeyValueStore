import os
import json
import redis
import socket
import threading
import time

class Replica():
    def __init__(self,id, recvHost, recvPort, redisHost, redisPort, otherReplicas):
        '''
        Description: Init method
        '''
        print(f"Inside Replica constructor {id}")
        self.id = int(id)
        self.host = recvHost
        self.port = recvPort
        self.redisHost = redisHost
        self.redisPort = redisPort
        self.otherReplicas = otherReplicas
        self.dataStore = redis.Redis(host=self.redisHost,port=self.redisPort)
        self.checkRedis()
        self.run()
        
    def log(self,message):
        print(f"> {self.id}: ",message)
        
    def checkRedis(self):
        if self.dataStore.ping():
            self.log(f"redis working on port:{self.redisPort}")
    
    def send(self,host,port,message):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.sendall(bytes(message, "utf-8"))
            sock.close()
            return True
        except Exception as E:
            print(str(E))
            return False
        
    def broadCast(self, msg):
        failed = 0
        for replica in self.otherReplicas:
            if not self.send(replica["replicaHost"],replica["replicaPort"],msg):
                self.log(f"failed sending data to [{replica['id']}] {replica['port']}")
                failed+=1
        return failed
    
    
    def handleSetRequest(self,key,value):
        try:
            self.dataStore.set(key,value)
            return True
        except Exception as e:
            print(str(e))
            return False
        
    def handleGetRequest(self,key):
        try:
            value = self.dataStore.get(key)
            if value is not None:
                return value.decode("utf-8")
            return None
        except Exception as e:
            print(str(e))
            return False
    
    def messageDispatcher(self,message):
        msgList = message.split(" ")
        request_type = msgList[2]
        client_host = msgList[0]
        client_port = int(msgList[1])
        if request_type == "set":
            broadcast = msgList[6]
            key = msgList[4]
            value = msgList[5]
            self.handleSetRequest(key, value)
            if broadcast == "True":
                time.sleep(1)
                msg = f"{client_host} {client_port} set {msgList[3]} {key} {value} False"
                failed = self.broadCast(msg)
                if failed == 0:
                    print("Updates sent to all replicas")
                    if self.send(client_host, client_port, f"Key {key} with a value of {value} set to the store."):
                        print(f"Response sent to {client_host}:{client_port}")
                    
                else:
                    print(f"Failed to send updates to {failed} replicas")
                    
            else:
                print('Store Updated locally')
                
            
        elif request_type == "get":
            value = self.handleGetRequest(msgList[4])
            self.send(client_host, client_port, f"Value of key {msgList[4]} is {value}")
            
            
    
    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host,self.port))
        sock.listen(10)
        self.log(f"is listening on {self.host}:{self.port}")
        while True:
            sck,addr = sock.accept()
            data = sck.recv(1024)
            self.messageDispatcher(data.decode("utf-8")) 
            
            
    def run(self):
        self.log(f"{self.id} is listening on port {self.port}.")
        listenThread = threading.Thread(target=self.listen, args=()).start()