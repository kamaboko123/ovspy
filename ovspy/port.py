import copy

class OvsPort():
    def __init__(self, uuid):
        self.id = uuid
    
    def set_client(self, client):
        self.ovs_client = client
    
    def get_uuid(self):
        return self.id
    
    #def get_info(self):
    #    return copy.deepcopy(self.ovs_client.get_port_raw(port_id=self.id))
    
    def get_name(self):
        target_port = self.ovs_client.get_port_raw(port_id=self.id)
        return target_port["name"]
    
    def is_internal(self):
        target_port = self.ovs_client.get_port_raw(port_id=self.id)
        _interface = self.ovs_client.get_interface_raw(interface_id=target_port["interfaces"][1])
        
        return _interface["type"] == "internal"
    
    def get_vlan_info(self):
        target_port = self.ovs_client.get_port_raw(port_id=self.id)
        
        if isinstance(target_port["tag"], list):
            tags = None
            if isinstance(target_port["trunks"], int):
                tags = [target_port["trunks"]]
            elif isinstance(target_port["trunks"], list):
                tags = target_port["trunks"][1]
            return {
                "mode":"trunk",
                "tag": tags
            }
        elif isinstance(target_port["tag"], int):
            return {
                "mode":"access",
                "tag":target_port["tag"]
            }
        
        raise ovspy_error.Unsupported("The VLAN configuration parameters is unsupported ovspy. (%s)", target_port)
    
    def get_raw(self):
        return self.ovs_client.get_port_raw(port_id=self.get_uuid())
    
