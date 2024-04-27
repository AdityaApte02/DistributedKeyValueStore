import hashlib
class RequestMessage():
    def __init__(self, client_id, client_time, senderId, host, port, messageType, replica):
        self.client_id = client_id
        self.client_time = client_time
        self.senderId = senderId
        self.senderHost = host
        self.senderPort = port
        self.messageType = messageType
        self.replica = replica
        self.hash = str(client_id) + "_" + str(client_time)
        self.acks = 0
        
    # def __lt__(self, other):
    #     if self.client_time == other.client_time:
    #         return self.client_id < other.client_id
    #     return self.client_time < other.client_time
    
    
    def __str__(self) -> str:
        return self.messageType + ' ' + str(self.client_id) + ' ' + str(self.client_time)
        
    def serialize(self):
        return "MSG " + self.messageType+ f" {self.client_id} {self.client_time} {self.senderId} " +  self.senderHost + f" {self.senderPort}" + f" {self.replica}"
        
class SetMessage(RequestMessage):
    def __init__(self,  client_id, client_time, senderId, host, port, key, value, replica, broadcast, messageType ="set"):
        super().__init__(client_id, client_time, senderId, host, port, messageType, replica)
        self.key = key
        self.value = value
        self.broadcast = broadcast
        
        
    def __str__(self) -> str:
        return super().__str__() + " " + self.key + " " + self.value 
        
    def serialize(self):
        return super().serialize() + f" {self.key} {self.value} {self.broadcast}"
    
    
    @staticmethod
    def deserialize(message):
        msgList = message.split(" ")
        messageType = msgList[1]
        client_id = msgList[2]
        client_time = msgList[3]
        senderId = msgList[4]
        senderHost = msgList[5]
        senderPort = msgList[6]
        replica = msgList[7]
        key = msgList[8]
        value = msgList[9]
        broadcast = msgList[10]
        
        return SetMessage(client_id, client_time, senderId, senderHost, senderPort,  key, value, replica, broadcast, messageType)
        
        
class GetMessage(RequestMessage):
    def __init__(self, client_id, client_time, senderId, host, port, key, replica, broadcast, messageType = "get"):
        super().__init__(client_id, client_time, senderId, host, port, messageType, replica)
        self.key = key
        self.broadcast = broadcast
        
    def __str__(self) -> str:
        return super().__str__() + " " + self.key
        
    def serialize(self):
        return super().serialize() + f" {self.key} {self.broadcast}"
    
    @staticmethod
    def deserialize(message):
        msgList = message.split(" ")
        messageType = msgList[1]
        client_id = msgList[2]
        client_time = msgList[3]
        senderId = msgList[4]
        senderHost = msgList[5]
        senderPort = msgList[6]
        replica = msgList[7]
        key = msgList[8]
        broadcast = msgList[9]
        
        return GetMessage(client_id, client_time, senderId, senderHost, senderPort, key, replica, broadcast, messageType)
    
    
    

class Acknowledgement():
    def __init__(self, client_id, client_time, senderId, host, port, hashValue) -> None:
        self.client_id = client_id
        self.client_time = client_time
        self.senderId = senderId
        self.senderHost = host
        self.senderPort = port
        self.hash = hashValue
        
    def serialize(self):
        return "ACK " + f"{self.client_id} {self.client_time} {self.senderId} "+ self.senderHost + f" {self.senderPort}" + f" {self.hash}"
    
    
    @staticmethod
    def deserialize(message):
        msgList = message.split(" ")
        client_id = msgList[1]
        client_time = msgList[2]
        senderId = msgList[3]
        senderHost = msgList[4]
        senderPort = msgList[5]
        hashValue = msgList[6]
        
        return Acknowledgement(client_id, client_time, senderId, senderHost, senderPort, hashValue)

