import ipaddress
import socket
import json
from . import ovsdb_query
from .bridge import OvsBridge
from .port import OvsPort
from datetime import datetime, timedelta
import sys
import time

class OvsClient:
    SEND_DEBUG = False
    RECV_DEBUG = False
    
    def __init__(self, ovsdb_port, ovsdb_ip="127.0.0.1"):
        self._ovsdb_ip = ipaddress.ip_address(ovsdb_ip)
        self._ovsdb_port = int(ovsdb_port)
        self._query_timeout = 5
    
    def _send(self, query):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((str(self._ovsdb_ip), self._ovsdb_port))
        
        if self.SEND_DEBUG:
            sys.stderr.write("[SEND] %s\n" % json.dumps(query).encode())
        s.send(json.dumps(query).encode())
        #s.shutdown(socket.SHUT_RDWR)
        
        buf = bytes()
        bufsize = 16
        
        timeout = datetime.now() + timedelta(seconds=self._query_timeout)
        while True:
            if datetime.now() >= timeout:
                raise Exception("Timeout")
            
            buf += s.recv(bufsize)
            
            try:
                query_result = json.loads(buf.decode())
                
                #echo method
                #https://tools.ietf.org/html/rfc7047
                if "method" in query_result.keys() and query_result["method"] == "echo":
                    echo_reply= {
                        "method": "echo",
                        "params": query_result["params"],
                        "id": query_result["id"]
                    }
                    s.send(json.loads(echo_reply).encode())
                    buf = bytes()
                    continue
                else:
                    break
            except json.JSONDecodeError:
                pass
        
        s.close()
        
        if self.RECV_DEBUG:
            sys.stderr.write("[RECV] %s\n" % query_result)
        
        self._check_error(query_result)
        return query_result
    
    @staticmethod
    def _check_error(query_result_json):
        if "result" in query_result_json.keys():
            for item in query_result_json["result"]:
                if "error" in item.keys():
                    raise Exception("[QueryError] %s" % item["details"])
        elif len(query_result_json["error"]) != 0:
            raise Exception("[QueryError] %s" % query_result_json["error"])
    
    def get_bridge_raw(self, bridge_id=None):
        query = ovsdb_query.Generator.get_bridges()
        
        result = self._send(query)
        
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
        bridge_raw = bridge.get_raw()
        if bridge_raw is None:
            raise Exception("bridge is not found")
        
        if self.find_port(port_name) is not None:
            raise Exception("port is already exist")
        
        #print(bridge.get_raw())
        
        exist_ports = []
        for p in bridge.get_ports():
            exist_ports.append(p.get_uuid())
        
        query = ovsdb_query.Generator.add_port(bridge.get_uuid(), exist_ports, port_name, vlan=vlan)
        self._send(query)
    
    def del_port_from_bridge(self, bridge, port_name):
        target_port = bridge.find_port(port_name)
        
        exist_ports = []
        for p in bridge.get_ports():
            exist_ports.append(p.get_uuid())
        exist_ports = list(set(exist_ports))
        
        if target_port is None:
            raise Exception("Specified port(%s) is not exist in bridge(%s)." % (port_name, bridge.get_name()))
        if target_port.get_uuid() not in exist_ports:
            raise Exception("Specified port(%s) is not exist in bridge(%s)." % (port_name, bridge.get_name()))
        
        query = ovsdb_query.Generator.del_port(bridge.get_uuid(), exist_ports, target_port.get_uuid())
        self._send(query)
        
