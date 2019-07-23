
class OvsBridge():
    def __init__(self, uuid):
        self.id = uuid
        
    def set_client(self, client):
        self.ovs_client = client
    
    def get_uuid(self):
        return self.id
    
    def get_ports(self, client):
        pass

