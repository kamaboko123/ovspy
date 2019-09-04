import uuid
import random

class Generator():
    
    id_min = 0
    id_max = 10000
    
    @staticmethod
    def get_bridges():
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
            "id": random.randint(Generator.id_min, Generator.id_max)
        }
        
        return query
    
    @staticmethod
    def get_ports():
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
            "id": random.randint(Generator.id_min, Generator.id_max)
        }
        
        return query
    
    @staticmethod
    def add_port(bridge_id, exist_port_id_list, new_port_name, vlan=None):
        
        #generate temporary values for query string needs
        interface_tmp_id = "row%s" % str(uuid.uuid4()).replace("-", "_")
        port_tmp_id = "row%s" % str(uuid.uuid4()).replace("-", "_")
        
        #generate new port list
        ports = []
        for p_id in exist_port_id_list:
            ports.append(["uuid", p_id])
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
                        "name":new_port_name,
                        #"type":""
                    }
                },
                {
                    "uuid-name": port_tmp_id,
                    "op" : "insert",
                    "table" : "Port",
                    "row":{
                        "name" : new_port_name,
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
                                bridge_id
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
            "id": random.randint(Generator.id_min, Generator.id_max)
        }
        
        if vlan is not None:
            if isinstance(vlan, int):
                query["params"][2]["row"].update({"tag":vlan})
            elif isinstance(vlan, list):
                query["params"][2]["row"].update({"tag":["set", []], "trunks":["set", vlan]})
            else:
                raise ValueError("Invalid VLAN type or format was specified.")
        return query
    
    @staticmethod
    def del_port(bridge_id, bridge_port_id_list, target_port_id):
        bridge_port_id_list.remove(target_port_id)
        new_ports = []
        for p in bridge_port_id_list:
            new_ports.append(["uuid", p])
        
        ret = {
            "id": 2,
            "method": "transact",
            "params": [
                "Open_vSwitch",
                {
                    "where": [
                        [
                            "_uuid",
                            "==",
                            [
                                "uuid",
                                bridge_id
                            ]
                        ]
                    ],
                    "row": {
                        "ports": [
                            "set",
                            new_ports
                        ]
                    },
                    "op": "update",
                    "table": "Bridge"
                }
            ]
        }
        
        return ret
    

