
from .port import OvsPort

class OvsBridge():
    def __init__(self, uuid):
        self.id = uuid
        
    def set_client(self, client):
        self.ovs_client = client
    
    def get_uuid(self):
        return self.id
    
    def get_ports(self):
        target_bridge = self.ovs_client.get_bridge_raw(bridge_id=self.id)
        
        ret = []
        #If ports is exist at the bridge, 'set' is store at ["port"][0]
        #'set' is not exist, the bridges doesn't have ports
        if target_bridge["ports"][0] == 'set':
            for port in target_bridge["ports"][1]:
                print(port)
                _port = OvsPort(port[1])
                _port.set_client(self.ovs_client)
                ret.append(_port)
        
        return ret
    
    def find_port(self, port_name):
        for p in self.get_ports():
            if p.get_name() == port_name:
                return p
        return None
    
    def get_name(self):
        target_bridge = self.ovs_client.get_bridge_raw(bridge_id=self.id)
        return target_bridge['name']
    
    def add_ports(self, port_name, vlan=None):
        if self.ovs_client.find_bridge(self.get_name()) is None:
            raise Exception("bridge is not found")
        
        if self.find_port(port_name) is not None:
            raise Exception("port is already exist")
    
    def del_ports(self, port_name, vlan=None):
        pass
