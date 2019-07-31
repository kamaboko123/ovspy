#!/usr/bin/python
#-*- coding: utf-8 -*-

#OVSDB Manipulation library for Python

import socket
import json
import ipaddress
import uuid
from pprint import pprint

RCV_BUF = 8192

class OvsdbClient:
    
    _ovsdb_ip = None
    _ovsdb_port = None
    
    _transact_id = 0
    
    def __init__(self, ovsdb_port, ovsdb_ip="127.0.0.1"):
        self._ovsdb_ip = ipaddress.ip_address(unicode(ovsdb_ip))
        self._ovsdb_port = int(ovsdb_port)
    
    def _send(self, query):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((str(self._ovsdb_ip), self._ovsdb_port))
        
        s.send(json.dumps(query))
        
        response = bytearray()
        while True:
            buf = byte_array(s.recv(64))
            if len(buf) == 0:
                break
            response.append(buf)
        
        response = bytes(response)
        
        return json.loads(response)
    
    def get_ports(self):
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
        
        return result["result"][0]["rows"]
    
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
        
        ret = {}
        return result["result"][0]["rows"]
    
    """
    def get_bridge_config(self):
        bridges = self.get_bridges()
        ports = self.get_ports()
        
        print bridges
        print ports
        
        ret = {}
        
        for br in bridges:
            ret[br["name"]] = {
                "ports" : {}
            }
            
            for port_uuid in br["ports"]:
                if port_uuid == "set":
                    continue
                ret[br["name"]]["ports"][port_uuid] = ports[port_uuid]
            
        return ret
    """
    
    def get_interfaces(self):
        query = {
            "method":"transact",
            "params":[
                "Open_vSwitch",
                {
                    "op" : "select",
                    "table" : "Interface",
                    "where" : [],
                }
            ],
            "id":0
        }
        
        result = self._send(query)
        
        #pprint(result["result"][0]["rows"])
        return(result["result"][0]["rows"])
    
    def add_interface(self, bridge_name, interface_name, vlan=None):
        for interface in self.get_interfaces():
            if interface_name == interface["name"]:
                raise Exception("the interface already exisit %s" % interface_name)
            if interface["type"] == "internal":
                continue
            print("%s : %s" % (interface["name"], interface["_uuid"]))
        
        print
        target_bridge = None
        ports = []
        for bridge in self.get_bridges():
            print("%s : %s" % (bridge["name"], bridge["_uuid"]))
            if bridge_name == bridge["name"]:
                target_bridge = bridge["_uuid"][1]
                ports.append(bridge["ports"])
                #print("!!%s" % bridge["ports"])
        
        if target_bridge is None:
            raise Exception("the bridge is not found : %s" % bridge_name)
        
        print target_bridge
        interface_tmp_id = "row%s" % str(uuid.uuid4()).replace("-", "_")
        port_tmp_id = "row%s" % str(uuid.uuid4()).replace("-", "_")
        
        ports.append(["named-uuid", port_tmp_id])
        
        query = {
            "method":"transact",
            "params":[
                "Open_vSwitch",
                {
                    "uuid-name" : interface_tmp_id,
                    "op" : "insert",
                    "table" : "Interface",
                    "row":{
                        "name":interface_name,
                        "type":""
                    }
                },
                {
                    "uuid-name": port_tmp_id,
                    "op" : "insert",
                    "table" : "Port",
                    "row":{
                        "name" : interface_name,
                        "interfaces":[
                            "named-uuid",
                            interface_tmp_id
                        ]
                    }
                },
                {
                    "where": [
                        [
                            "_uuid",
                            "==",
                            [
                                "uuid",
                                target_bridge
                            ]
                        ]
                    ],
                    "row": {
                        "ports": [
                            "set",
                            ports
                        ]
                    },
                    "op": "update",
                    "table": "Bridge"
                }
            ],
            "id":self._transact_id
        }
        self._transact_id += 1
        
        if isinstance(vlan, list):
            query["params"][2]["row"]["trunks"] = ["set", vlan]
            #raise Exception("not supported configure trunk port")
        if isinstance(vlan, int):
            query["params"][2]["row"]["tag"] = vlan
        
        pprint(query)
        result = self._send(query)
        
        pprint(result)
    
    def del_interface(self, bridge_name, interface_name):
        target_bridge = None
        for br in self.get_bridges():
            if br["name"] == bridge_name:
                target_bridge = br
        
        if target_bridge is None:
            raise Exception("the bridge is not found : %s" % bridge_name)
        
        print target_bridge
        
        target_port = None
        
        for port in self.get_ports():
            if port["name"] == interface_name:
                target_port = port
        
        if target_port is None:
            raise Exception("the interface is not found : %s" % interface_name)
        
        print target_port
        
        find_port = False
        br_ports = target_bridge["ports"][1]
        for port in br_ports:
            if port[1] == target_port["_uuid"][1]:
                find_port = True
        
        if not find_port :
            raise Exception("interface \"%s\" is not attached to bridge \"%s\"." % (interface_name, bridge_name))
        
        
        set_port = []
        
        for port in target_bridge["ports"][1]:
            if port[1] == target_port["_uuid"][1]:
                continue
            set_port.append(port)
        
        print set_port
        
        query = {
            "method":"transact",
            "params":[
                "Open_vSwitch",
                {
                    "where": [
                        [
                            "_uuid",
                            "==",
                            [
                                "uuid",
                                target_bridge["_uuid"][1]
                            ]
                        ]
                    ],
                    "row": {
                        "ports": [
                            "set",
                            set_port
                        ]
                    },
                    "op": "update",
                    "table": "Bridge"
                }
            ],
            "id":self._transact_id
        }
        self._transact_id += 1
        
        pprint(query)
        result = self._send(query)
        
        pprint(result)
    
if __name__ == '__main__':
    ovsdb = OvsdbClient(5678)
    
    #ovsdb.get_interface()
    #ovsdb.add_interface("ovs-docker", "enp2s0", [100,200])
    #ovsdb.add_interface("ovs-docker", "enp4s0")
    #ovsdb.del_interface("ovs-docker", "enp4s0")
