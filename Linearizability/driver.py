from replicaDriver import ReplicaDriver
from clientDriver import ClientDriver
import time
class Driver():
    def __init__(self):
        self.run()
        
    def run(self):
        ReplicaDriver()
        time.sleep(2)
        ClientDriver()
        time.sleep(0.1)
        print(f"Started the Clients and the Replicas")
    
    
if __name__ == "__main__":
    driver = Driver()