import multiprocessing
from replica import Replica
import time
import os
import json

class ReplicaDriver():
    def __init__(self,numReplicas):  
        '''
        Call the Driver run method which spawns the replicas.
        '''
        self.configPath = os.path.join(os.getcwd(), "EventualConsistency", "config.json")     
        self.run()
            
            
    def readConfig(self):
        '''
        Description: Reads the config file.
        '''
        with open(self.configPath, "r") as file:
            jsonData = json.loads(file.read())
        return jsonData
            
    def run(self):
        '''
        Description: The run method of the driver class.
        '''
        data = self.readConfig()
        self.num_of_replicas = len(data)
        for i in range(self.num_of_replicas):
            otherReplicas = list(filter(lambda obj: obj['id'] != i+1, data))
            if not self.spawnReplica(i+1, data[i]["replicaHost"], data[i]["replicaPort"], data[i]["redisHost"], data[i]["redisPort"], otherReplicas):
                break
    
    def spawnReplica(self,id, recvHost, recvPort, redisHost, redisPort, otherReplicas):
        try:
            multiprocessing.Process(target=Replica,args=(id, recvHost, recvPort, redisHost, redisPort, otherReplicas)).start()
            time.sleep(.01)
            print(f"Replica {id}")
            return True
        except Exception as e:
            print(str(e))
            return False
            

if __name__ == "__main__":
    ReplicaDriver(3)
        
    