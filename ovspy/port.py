import copy

class OvsPort():
    def __init__(self, uuid):
        self.id = uuid
    
    def set_client(self, client):
        self.ovs_client = client
    
    def get_uuid(self):
        return self.id
    
    def get_info(self):
        return copy.deepcopy(self.ovs_client.get_port_raw(port_id=self.id))
    
    def get_name(self):
        target_port = self.ovs_client.get_port_raw(port_id=self.id)
        return target_port["name"]
    
    def get_vlan_info(self):
        target_port = self.ovs_client.get_port_raw(port_id=self.id)
        
        if isinstance(target_port["tag"], list):
            return {
                "mode":"trunk",
                "tag": target_port["trunks"][1]
            }
        elif isinstance(target_port["tag"], int):
            return {
                "mode":"access",
                "tag":target_port["tag"]
            }
        
        raise Exception("")
    
    def get_raw(self):
        return self.ovs_client.get_port_raw(port_id=self.get_uuid())
    
