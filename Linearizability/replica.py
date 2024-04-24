import os
import json
import redis
import socket
import threading
import time
import heapq
from message import SetMessage, GetMessage

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
        self.queue = []
        self.ack_list = []
        self.ack_dict = {}
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
        try:
            msgList = message.split(" ")
            msg_type = msgList[0]
            if msg_type == "MSG":
                request_type = msgList[1]
                if request_type == "set":
                    setMessageObj = SetMessage.deserialize(message)
                    if setMessageObj.broadcast == "True":
                        time.sleep(1)
                        self.handleSetRequest(setMessageObj.key, setMessageObj.value)
                        setMessageObj.broadcast = "False"
                        msg = setMessageObj.serialize()
                        failed = self.broadCast(msg)
                        if failed == 0:
                            print("Updates sent to all replicas")
                            if self.send(setMessageObj.senderHost, int(setMessageObj.senderPort), f"Key {setMessageObj.key} with a value of {setMessageObj.value} set to the store."):
                                print(f"Response sent to {setMessageObj.senderHost}:{setMessageObj.senderPort}")
                            
                        else:
                            print(f"Failed to send updates to {failed} replicas")
                            
                    else:
                        print("Store updated Locally")
                        
                    
                elif request_type == "get":
                    getMessageObj = GetMessage.deserialize(message)
                    value = self.handleGetRequest(getMessageObj.key)
                    self.send(getMessageObj.senderHost, int(getMessageObj.senderPort), f"Value of key {getMessageObj.key} is {value}")
                
                
            elif msg_type == "ACK":
                pass
            
        except Exception as e:
            print(str(e))
    
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
        self.dataStore.flushall()
        time.sleep(1)
        self.log(f"{self.id} is listening on port {self.port}.")
        listenThread = threading.Thread(target=self.listen, args=()).start()