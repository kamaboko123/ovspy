import ipaddress
import socket
import json
from . import ovsdb_query
from .bridge import OvsBridge
from .port import OvsPort
import re

class OvsClient:
    SEND_DEBUG = False
    RECV_DEBUG = False
    def __init__(self, ovsdb_port, ovsdb_ip="127.0.0.1"):
        self._ovsdb_ip = ipaddress.ip_address(ovsdb_ip)
        self._ovsdb_port = int(ovsdb_port)
    
    def _send(self, query):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((str(self._ovsdb_ip), self._ovsdb_port))
        
        if self.SEND_DEBUG:
            print("[SEND] %s" % json.dumps(query).encode())
        s.send(json.dumps(query).encode())
        #s.shutdown(socket.SHUT_RDWR)
        
        buf = bytes()
        bufsize = 16
        
        while True:
            buf += s.recv(bufsize)
            
            try:
                query_result = json.loads(buf.decode())
                
                #TODO: implement echo method
                #[temporary]skip echo method(based JSON-RPC)
                #https://tools.ietf.org/html/rfc7047
                if "method" in query_result.keys() and query_result["method"] == "echo":
                    buf = bytes()
                    continue
                
                break
            except json.JSONDecodeError:
                pass
            
        s.close()
        
        if self.RECV_DEBUG:
            print("[RECV] %s" % query_result)
        
        self._check_error(query_result)
        
        if "error" not in query_result.keys() or query_result["error"] is not None:
            raise Exception("Query error. %s" % query_result)
        
        return query_result
    
    @staticmethod
    def _check_error(query_result_json):
        for item in query_result_json["result"]:
            if "error" in item.keys():
                raise Exception("[QueryError] %s" % item["details"])
    
    def get_bridge_raw(self, bridge_id=None):
        query = ovsdb_query.Generator.get_bridges()
        
        result = self._send(query)
        
        #if result is None:
        #    return []
        
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
    
    def find_port(self, port_name):
        for p in self.get_port_raw():
            if p["name"] == port_name:
                return p
        return None
    
    def get_port_raw(self, port_id=None):
        
        query = ovsdb_query.Generator.get_ports()
        
        result = self._send(query)
        
        if port_id is not None:
            for p in result["result"][0]["rows"]:
                if p['_uuid'][1] == port_id:
                    return p
        else:
            return result["result"][0]["rows"]
        
        return None
    
    def add_port_to_bridge(self, bridge, port_name, vlan=None):
        target_bridge = bridge.get_raw()
        if target_bridge is None:
            raise Exception("bridge is not found")
        
        if self.find_port(port_name) is not None:
            raise Exception("port is already exist")
        
        query = ovsdb_query.Generator.add_port(bridge.get_uuid(), target_bridge["ports"][1], port_name, vlan=vlan)
        
        print(self._send(query))
    
    def del_port_from_bridge(self):
        pass
