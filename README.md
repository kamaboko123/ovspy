# ovspy
Open vSwitch Library written in Python  


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

### Sample code
```
>>> import ovspy.client
>>> ovs = ovspy.client.OvsClient(5678)
>>> ovs.get_bridge()
[<ovspy.bridge.OvsBridge object at 0x7f3197bc1fd0>]
>>> ovs.get_bridge()[0].get_name()
'br0'
```

