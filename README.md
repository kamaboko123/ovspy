# ovspy
Open vSwitch Library written in Python  

[ovspy · PyPI](https://pypi.org/project/ovspy/)

## Supported Operation
- Bridge
  - Get(name, uuid, port)
  - Add
  - Delete
- Port
  - Get(name, uuid, vlan)
  - Add(with VLAN)
  - Delete

## install
```
pip install ovspy
```

## Getting Started

### Configure Open vSwitch Manager
This library manipulate Open vSwitch by access OVSDB  
You need to configure OVSDB manager port to manipulate OVSDB by TCP.
```
sudo ovs-vsctl set-manager ptcp:5678
```

### Bridge
```
import ovspy.client

ovs = ovspy.client.OvsClient(5678)

#Get exist all bridges
#This function return list of OvsBridge instance
for br in ovs.get_bridges():
    print(br.get_name())

#Find bridge by bridge name
#This function return OvsBridge instance
#If specified bridge is not found, the function return None
bridge = ovs.find_bridge("br0")
print(bridge.get_name())


#Add bridge
#If specified bridge is already exist, This function raise ovspy.ovs_error.Duplicate
ovs.add_bridge("br1")

#Delete bridge
#If specified bridge is not exist, This function raise ovspy.ovs_error.NotFound
ovs.del_bridge("br1")
```

### Port
```
import ovspy.client

ovs = ovspy.client.OvsClient(5678)

#Get Bridge instance
bridge = ovs.find_bridge("br0")

#Get all ports which is associate to birgde
for p in bridge.get_ports():
    print("%s:(%s)" % (p.get_name(), p.get_vlan_info()))

#Find port by name
port =  bridge.find_port("p0")
print(port.get_name())

#Add port(Access port)
bridge.add_port("p1", 10)

#Add port(Trunk port)
bridge.add_port("p2")
bridge.add_port("p3", [])

#Add port(Trunk port with restrict vlan)
bridge.add_port("p4", [10, 20])

#Delete port(Trunk port with restrict vlan)
bridge.del_port("p3")

```

### Errors
ovspy has as following class as custom exception
- `ovspy.ovs_error.OvspyError`
  - Super class of custom exceptions
- `ovspy.ovs_error.Duplicate`
  - The error is raise when user operation cause duplicate status(e.g. Case of try to create port with same name as existing port)
- `ovspy.ovs_error.NotFound`
  - The error is raise when user specified resource is not exist. (e.g. Case of try to delete port but the port is not existing)
- `ovspy.ovs_error.TransactionError`
  - The error is raise when failed to transaction with OVSDB. (e.g. Timeout for connection)
- `ovspy.ovs_error.Unsupported`
  - The error is raise when user try to unsupported operation with ovspy.


