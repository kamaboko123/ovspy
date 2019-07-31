import ipaddress
import socket
import json
from .bridge import OvsBridge
from .port import OvsPort
import re

class OvsClient:
    def __init__(self, ovsdb_port, ovsdb_ip="127.0.0.1"):
        self._ovsdb_ip = ipaddress.ip_address(ovsdb_ip)
        self._ovsdb_port = int(ovsdb_port)
    
    def _send(self, query):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((str(self._ovsdb_ip), self._ovsdb_port))
        
        s.send(json.dumps(query).encode())
        s.shutdown(socket.SHUT_RDWR)
        
        response = bytes()
        bufsize = 16
        while True:
            buf = s.recv(bufsize)
            
            #skip echo method(based JSON-RPC)
            #https://tools.ietf.org/html/rfc7047
            if re.search(r'"method":"echo"', buf.decode()) is not None:
                continue
            
            if len(buf) == 0:
                break
            
            response += buf
            
        s.close()
        return json.loads(response.decode())
    
    def get_bridge_raw(self, bridge_id=None):
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
        
        if bridge_id is None:
            return result["result"][0]["rows"]
        else:
            for br in result["result"][0]["rows"]:
                if br['_uuid'][1] == bridge_id:
                    return br
        
        return None
    
    def get_bridges(self):
        bridges = self.get_bridge_raw()
        ret = []
        
        for br in bridges:
            _br = OvsBridge(br['_uuid'][1])
            _br.set_client(self)
            ret.append(_br)
        
        return ret
    
    def find_bridge(self, bridge_name):
        for br in self.get_bridges():
            if br.get_name() == bridge_name:
                return br
        return None
    
    def get_port_raw(self, port_id=None):
        query = {
            "method":"transact",
            "params":[
                "Open_vSwitch",
                {
                    "op" : "select",
                    "table" : "Port",
                    "where" : [],
                }
            ],
            "id":0
        }
        
        result = self._send(query)
        
        if "error" not in result.keys() or result["error"] is not None:
            raise Exception("なんかのエラー")
        
        if port_id is not None:
            for p in result["result"][0]["rows"]:
                if p['_uuid'][1] == port_id:
                    return p
        else:
            return result["result"][0]["rows"]
        
        return None
    
