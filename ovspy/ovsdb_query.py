import uuid
import random

class Generator():
    
    id_min = 0
    id_max = 10000
    
    @staticmethod
    def get_ovs():
        query = {
            "method":"transact",
            "params":[
                "Open_vSwitch",
                {
                    "op" : "select",
                    "table" : "Open_vSwitch",
                    "where" : [],
                }
            ],
            "id": random.randint(Generator.id_min, Generator.id_max)
        }
        
        return query
    
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
            "id": random.randint(Generator.id_min, Generator.id_max),
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
    
    @staticmethod
    def add_bridge(ovs_id, bridge_name, exist_bridge_id_list):
        #generate temporary values for query string needs
        bridge_tmp_id = "row%s" % str(uuid.uuid4()).replace("-", "_")
        inital_port_tmp_id = "row%s" % str(uuid.uuid4()).replace("-", "_")
        inital_interface_tmp_id = "row%s" % str(uuid.uuid4()).replace("-", "_")
        
        bridges = []
        for br_id in exist_bridge_id_list:
            bridges.append(["uuid", br_id])
        bridges.append(["named-uuid", bridge_tmp_id])
        
        ret = {
            "id": random.randint(Generator.id_min, Generator.id_max),
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
                                ovs_id
                            ]
                        ]
                    ],
                    "row": {
                        "bridges": [
                            "set",
                            bridges
                        ]
                    },
                    "op": "update",
                    "table": "Open_vSwitch"
                },
                {
                    "uuid-name": inital_port_tmp_id,
                    "row": {
                        "name": bridge_name,
                        "interfaces": [
                            "named-uuid",
                            inital_interface_tmp_id
                        ]
                    },
                    "op": "insert",
                    "table": "Port"
                },
                {
                    "uuid-name": bridge_tmp_id,
                    "row": {
                        "name": bridge_name,
                        "ports": [
                            "named-uuid",
                            inital_port_tmp_id
                        ]
                    },
                    "op": "insert",
                    "table": "Bridge"
                },
                {
                    "uuid-name": inital_interface_tmp_id,
                    "row": {
                        "name": bridge_name,
                        "type": "internal"
                    },
                    "op": "insert",
                    "table": "Interface"
                },
            ]
        }
        
        return ret
    
    @staticmethod
    def del_bridge(ovs_id, bridge_id_list, target_bridge_id):
        bridge_id_list.remove(target_bridge_id)
        new_bridges = []
        for br in bridge_id_list:
            new_bridges.append(["uuid", br])
        
        ret = {
            "id": random.randint(Generator.id_min, Generator.id_max),
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
                                ovs_id
                            ]
                        ]
                    ],
                    "row": {
                        "bridges": [
                            "set",
                            new_bridges
                        ]
                    },
                    "op": "update",
                    "table": "Open_vSwitch"
                }
            ]
        }
        
        return ret
