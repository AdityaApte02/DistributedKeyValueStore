import hashlib
class RequestMessage():
    def __init__(self, msg_id, msg_time, senderId, host, port, messageType, replica):
        self.msg_id = msg_id
        self.msg_time = msg_time
        self.senderId = senderId
        self.senderHost = host
        self.senderPort = port
        self.messageType = messageType
        self.replica = replica
        self.hash = str(msg_id) + "_" + str(msg_time)
        self.acks = 0
        
    def __lt__(self, other):
        return float(self.msg_time) < float(other.msg_time)
        
    def serialize(self):
        return "MSG " + self.messageType+ f" {self.msg_id} {self.msg_time} {self.senderId} " +  self.senderHost + f" {self.senderPort}" + f" {self.replica}"
        
class SetMessage(RequestMessage):
    def __init__(self,  msg_id, msg_time, senderId, host, port, key, value, replica, broadcast, messageType ="set"):
        super().__init__(msg_id, msg_time, senderId, host, port, messageType, replica)
        self.key = key
        self.value = value
        self.broadcast = broadcast
        
    def serialize(self):
        return super().serialize() + f" {self.key} {self.value} {self.broadcast}"
    
    
    @staticmethod
    def deserialize(message):
        msgList = message.split(" ")
        messageType = msgList[1]
        msg_id = msgList[2]
        msg_time = msgList[3]
        senderId = msgList[4]
        senderHost = msgList[5]
        senderPort = msgList[6]
        replica = msgList[7]
        key = msgList[8]
        value = msgList[9]
        broadcast = msgList[10]
        
        return SetMessage(msg_id, msg_time, senderId, senderHost, senderPort,  key, value, replica, broadcast, messageType)
        
        
class GetMessage(RequestMessage):
    def __init__(self, msg_id, msg_time, senderId, host, port, key, replica, broadcast, messageType = "get"):
        super().__init__(msg_id, msg_time, senderId, host, port, messageType, replica)
        self.key = key
        self.broadcast = broadcast
        
    def serialize(self):
        return super().serialize() + f" {self.key} {self.broadcast}"
    
    @staticmethod
    def deserialize(message):
        msgList = message.split(" ")
        messageType = msgList[1]
        msg_id = msgList[2]
        msg_time = msgList[3]
        senderId = msgList[4]
        senderHost = msgList[5]
        senderPort = msgList[6]
        replica = msgList[7]
        key = msgList[8]
        broadcast = msgList[9]
        
        return GetMessage(msg_id, msg_time, senderId, senderHost, senderPort, key, replica, broadcast, messageType)
    
    
    

class Acknowledgement():
    def __init__(self, msg_id, msg_time, senderId, host, port, hashValue) -> None:
        self.msg_id = msg_id
        self.msg_time = msg_time
        self.senderId = senderId
        self.senderHost = host
        self.senderPort = port
        self.hash = hashValue
        
    def serialize(self):
        return "ACK " + f"{self.msg_id} {self.msg_time} {self.senderId} "+ self.senderHost + f" {self.senderPort}" + f" {self.hash}"
    
    
    @staticmethod
    def deserialize(message):
        msgList = message.split(" ")
        msg_id = msgList[1]
        msg_time = msgList[2]
        senderId = msgList[3]
        senderHost = msgList[4]
        senderPort = msgList[5]
        hashValue = msgList[6]
        
        return Acknowledgement(msg_id, msg_time, senderId, senderHost, senderPort, hashValue)

