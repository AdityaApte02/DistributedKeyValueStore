import os
import json
from client import Client
import multiprocessing
class ClientDriver():
    def __init__(self):
        self.home_dir = os.path.join(os.getcwd(), "Clients")
        self.replica_config = os.path.join(os.getcwd(), "config.json")
        self.replicas = self.readReplicasConfig()
        self.run()
        
        
    def readReplicasConfig(self):
        try:
            with open(self.replica_config, "r") as file:
                jsonData = json.loads(file.read())
            return jsonData
        except Exception as e:
            print(str(e))
            return False
    
    def getClientConfig(self, path):
        try:
            with open(path, "r") as file:
                jsonData = json.loads(file.read())
            return jsonData
        except Exception as e:
            print(str(e))
            return False
    
    def spawnClient(self, id, replicas, requests, data, output_path):
        clientThread = multiprocessing.Process(target=Client, args=(id, replicas, requests, data, output_path)).start()

    def run(self):
        try:
            for i,dir_name in enumerate(os.listdir(self.home_dir)):
                cur_dir = os.path.join(self.home_dir, dir_name)
                if os.path.isdir(cur_dir):
                    output_path = os.path.join(cur_dir, "outputs.txt")
                    requests_path = os.path.join(cur_dir, "requests.json")
                    client_config_path = os.path.join(cur_dir, "client.json")
                    if os.path.exists(client_config_path):
                        data = self.getClientConfig(client_config_path)
                    if os.path.exists(requests_path):
                        with open(requests_path, "r") as file:
                            requests = json.loads(file.read())
                    self.spawnClient(i+1, self.replicas, requests, data, output_path)
        except Exception as e:
            print(str(e))
            return False
                
                
    