import hashlib
class RequestMessage():
    def __init__(self, msg_id, msg_time, host, port, messageType, replica):
        self.msg_id = msg_id
        self.msg_time = msg_time
        self.senderHost = host
        self.senderPort = port
        self.messageType = messageType
        self.replica = replica
        self.hash = hashlib.md5(f"{self.msg_id} {self.msg_time}".encode())
        self.acks = 0
        
    def serialize(self):
        return "MSG " + self.messageType+ f" {self.msg_id} {self.msg_time} " + self.senderHost + f" {self.senderPort}" + f" {self.replica}"
        
class SetMessage(RequestMessage):
    def __init__(self,  msg_id, msg_time, host, port, key, value, replica, broadcast, messageType ="set"):
        super().__init__(msg_id, msg_time, host, port, messageType, replica)
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
        senderHost = msgList[4]
        senderPort = msgList[5]
        replica = msgList[6]
        key = msgList[7]
        value = msgList[8]
        broadcast = msgList[9]
        
        return SetMessage(msg_id, msg_time, senderHost, senderPort,  key, value, replica, broadcast, messageType)
        
        
class GetMessage(RequestMessage):
    def __init__(self, msg_id, msg_time,host, port, key, replica, messageType = "get"):
        super().__init__(msg_id, msg_time, host, port, messageType, replica)
        self.key = key
        
    def serialize(self):
        return super().serialize() + f" {self.key}"
    
    @staticmethod
    def deserialize(message):
        msgList = message.split(" ")
        messageType = msgList[1]
        msg_id = msgList[2]
        msg_time = msgList[3]
        senderHost = msgList[4]
        senderPort = msgList[5]
        replica = msgList[6]
        key = msgList[7]
        
        return GetMessage(msg_id, msg_time, senderHost, senderPort, key, replica, messageType)
    
    
    
    
class Acknowledgement():
    def __init__(self, messageType, msg_id, msg_time, host, port) -> None:
        self.messsageType = messageType
        self.msg_id = msg_id
        self.msg_time = msg_time
        self.senderHost = host
        self.senderPort = port
        self.hash = hashlib.md5(f"{self.msg_id} {self.msg_time}".encode())
        
    def serialize(self):
        return "ACK " + self.senderHost + f" {self.senderPort} " + self.messsageType
        
        
class SetAcknowledgement(Acknowledgement):
    def __init__(self, msg_id, msg_time, host, port,messageType = "set_ack"):
        self.super().__init__(messageType, msg_id, msg_time, host, port)   
        
    def serialize(self):
        return self.super().serialize()
    
class GetAcknowledgement(RequestMessage):
    def __init__(self, msg_id, msg_time, host, port, messageType = "get_ack"):
        self.super().__init__(messageType, msg_id, msg_time, host, port)
        
    def serialize(self):
        return self.super().serialize()