# ovspy
Open vSwitch Library written in Python  

## Supported Configuraton
- Bridge
  - Add
  - Delete
- Port
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

for br in ovs.get_bridge():
    print(br.get_name())

#Find bridge by bridge name
#This function return OvsBridge instance
#If specified bridge is not found, the function return None

bridge = ovs.find_bridge("br0")
printf(bridge.get_name())


#Add bridge
#If specified bridge is already exist, This function raise ovspy.ovs_error.Duplicate
ovs.add_bridge("br1")

#Delete bridge
#If specified bridge is not exist, This function raise ovspy.ovs_error.NotFound
ovs.del_bridge("br1")
```

### Port

### Errors



