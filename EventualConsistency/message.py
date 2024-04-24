class Message():
    def __init__(self, host, port, messageType, replica):
        self.host = host
        self.port = port
        self.messageType = messageType
        self.replica = replica
       
        
    def serialize(self):
        return self.host + f" {self.port} " + self.messageType + f" {self.replica}"
        
class SetMessage(Message):
    def __init__(self,  host, port, key, value, replica, broadcast, messageType ="set"):
        super().__init__(host, port, messageType, replica)
        self.key = key
        self.value = value
        self.broadcast = broadcast
        
    def serialize(self):
        return super().serialize() + f" {self.key} {self.value} {self.broadcast}"
        
        
class GetMessage(Message):
    def __init__(self, host, port, key, replica, messageType = "get"):
        super().__init__(host, port, messageType, replica)
        self.key = key
        
    def serialize(self):
        return super().serialize() + f" {self.key}"
        