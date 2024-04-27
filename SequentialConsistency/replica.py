import os
import json
import redis
import socket
import threading
import time
import heapq
from message import SetMessage, GetMessage, Acknowledgement
import random
import copy

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
        self.num_replicas = len(otherReplicas) + 1
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
            
            
            
    def checkReplicaPorts(self, messageObj):
        for replica in self.otherReplicas:
            if int(messageObj.senderPort) == replica["replicaPort"]:
                return True 
        return False
            
            
    def processQueue(self):
        try:
            while True:
                if len(self.queue) > 0:
                    # self.log(self.queue)
                    if self.queue[0].acks >= self.num_replicas:
                        message = heapq.heappop(self.queue)
                        if message.messageType == "set":
                            self.handleSetRequest(message.key, message.value)
                            reply = f"Key {message.key} with a value of {message.value} set to the store."
                            if not self.checkReplicaPorts(message):
                                self.send(message.senderHost, int(message.senderPort), reply)
                        elif message.messageType =="get":
                            time.sleep(2)
                            value = self.handleGetRequest(message.key)
                            reply = f"Value of key {message.key} is {value}"
                            self.log(f"reply {reply}")
                            self.send(message.senderHost, int(message.senderPort), reply)
                        
                    else:
                        if self.queue[0].hash not in self.ack_dict:
                            self.log(f"ack_dict {list(self.ack_dict.keys())}")
                            ackObject = Acknowledgement(self.queue[0].client_id, self.queue[0].client_time, self.id, self.host, self.port, self.queue[0].hash)
                            self.broadCast(ackObject.serialize(),True)
                            self.ack_dict[ackObject.hash] = True
                            
                               
        except Exception as e:
            print(str(e))
    
    def send(self,host,port,message):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.sendall(bytes(message, "utf-8"))
            sock.close()
            return True
        except Exception as E:
            print(str(E) + " "+str(self.id))
            return False
        
    def broadCast(self, msg,sendToself=False):
        self.log(f"Broadcasting message {msg}")
        try:
            failed = 0
            for replica in self.otherReplicas:
                if not self.send(replica["replicaHost"],replica["replicaPort"],msg):
                    self.log(f"failed sending data to [{replica['id']}] {replica['port']}")
                    failed+=1
            if sendToself:
                if not self.send(self.host,self.port,msg):
                    failed+=1
            return failed
        
        except Exception as e:
            print(str(e))
            return False
    
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
        
        
    def logMessage(self, message):
        with open('./replica'+str(self.id)+'.txt', 'a') as file:
            file.write(message+'\n')
    
    def messageDispatcher(self,message):
        try:
            msgList = message.split(" ")
            msg_type = msgList[0]
        
            self.logMessage(message)
                
            if msg_type == "MSG":
                request_type = msgList[1]
                if request_type == "set":
                    setMessageObj = SetMessage.deserialize(message)
                    heapq.heapify(self.queue)
                    heapq.heappush(self.queue, copy.deepcopy(setMessageObj))
                    self.log(self.queue)
                    if setMessageObj.broadcast == "True":
                        # time.sleep(1)
                        setMessageObj.senderId = self.id
                        setMessageObj.senderHost = self.host
                        setMessageObj.senderPort = self.port
                        setMessageObj.broadcast = "False"
                        msg = setMessageObj.serialize()
                        failed = self.broadCast(msg)       
                        
                elif request_type == "get":
                    getMessageObj = GetMessage.deserialize(message)
                    getMessageObj.acks = self.num_replicas
                    heapq.heapify(self.queue)
                    heapq.heappush(self.queue, copy.deepcopy(getMessageObj))
                    self.log(self.queue)

                   
                
            elif msg_type == "ACK":
                ackObj = Acknowledgement.deserialize(message)
                self.log(f"Received an ack from {ackObj.senderId}")
                self.ack_list.append(ackObj)
                self.processAcks()
            
        except Exception as e:
            print(str(e))
            
            
            
    def processAcks(self):
        for messageObj in self.queue:
            for i in range(len(self.ack_list)):
                ackObj = self.ack_list[i]
                self.log(f"Comparing ack with hash {ackObj.hash} with message with hash {messageObj.hash} for {ackObj.senderId}")
                if messageObj.hash == ackObj.hash:
                    messageObj.acks += 1
                    self.log(f"Incrementing acks for message with hash {messageObj.hash} to {messageObj.acks}")
                    self.ack_list.pop(i)
                    break
        
    
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
        self.log(f"{self.id} is listening on port {self.port}.")
        listenThread = threading.Thread(target=self.listen, args=()).start()
        processQueueThread = threading.Thread(target=self.processQueue, args=()).start()