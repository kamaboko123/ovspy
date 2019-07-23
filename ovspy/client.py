import ipaddress
import socket
import json
from .bridge import OvsBridge

class OvsClient:
    def __init__(self, ovsdb_port, ovsdb_ip="127.0.0.1"):
        self._ovsdb_ip = ipaddress.ip_address(ovsdb_ip)
        self._ovsdb_port = int(ovsdb_port)
    
    def _send(self, query):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((str(self._ovsdb_ip), self._ovsdb_port))
        
        s.send(json.dumps(query).encode())
        response = s.recv(8192)
        
        return json.loads(response.decode())
    
    def get_bridges(self):
        query = {
            "method":"transact",
            "params":[
                "Open_vSwitch",
                {
                    "op" : "select",
                    "table" : "Bridge",
                    "where" : [],
                }
            ],
            "id":0
        }
        
        result = self._send(query)
        
        if "error" not in result.keys() or result["error"] is not None:
            raise Exception("なんかのエラー")
        
        ret = []
        for br in result["result"][0]["rows"]:
            _br = OvsBridge(br['_uuid'][1])
            _br.set_client(self)
            ret.append(_br)
            
        return ret
    
    def get_ports(self):
        pass

