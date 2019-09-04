import unittest
import subprocess
from ovspy.client import OvsClient


class TestOvspy(unittest.TestCase):
    def setUp(self):
        self.ovs = OvsClient(5678)
        self.ovs.SEND_DEBUG = True
        self.ovs.RECV_DEBUG = False
        
    def test_bridge(self):
        self.init_ovs()
        
        #check empty
        bridges = self.ovs.get_bridges()
        self.assertEqual(len(bridges), 0)
        
    
    def test_ports(self):
        self.init_ovs()
        
        bridge_name = "br0"
        cmd_del_all_bridge = "ovs-vsctl add-br %s" % bridge_name
        subprocess.run(cmd_del_all_bridge, shell=True)
        
        bridges = self.ovs.get_bridges()
        self.assertEqual(len(bridges), 1)
        
        bridge = bridges[0]
        self.assertEqual(bridge.get_name(), bridge_name)
        self.assertEqual(len(bridge.get_ports()), 1)
        
        bridge.add_port("p1")
        self.assertEqual(len(bridge.get_ports()), 2)
        
        bridge.add_port("p2", [])
        self.assertEqual(len(bridge.get_ports()), 3)
        
        bridge.add_port("p3", 3)
        self.assertEqual(len(bridge.get_ports()), 4)
        
        bridge.add_port("p4", 4)
        self.assertEqual(len(bridge.get_ports()), 5)
        
        bridge.add_port("p5", [5, 15])
        self.assertEqual(len(bridge.get_ports()), 6)
        
        bridge.add_port("p6", [6, 16])
        self.assertEqual(len(bridge.get_ports()), 7)
        
        self.assertEqual(bridge.find_port("p0"), None)
        self.assertEqual(bridge.find_port("p1").get_name(), "p1")
        self.assertEqual(bridge.find_port("p2").get_name(), "p2")
        self.assertEqual(bridge.find_port("p3").get_name(), "p3")
        self.assertEqual(bridge.find_port("p4").get_name(), "p4")
        self.assertEqual(bridge.find_port("p5").get_name(), "p5")
        self.assertEqual(bridge.find_port("p6").get_name(), "p6")
        
        self.assertEqual(bridge.find_port("p1").get_vlan_info(), {"mode":"trunk","tag":[]})
        self.assertEqual(bridge.find_port("p2").get_vlan_info(), {"mode":"trunk","tag":[]})
        self.assertEqual(bridge.find_port("p3").get_vlan_info(), {"mode":"access","tag":3})
        self.assertEqual(bridge.find_port("p4").get_vlan_info(), {"mode":"access","tag":4})
        self.assertEqual(bridge.find_port("p5").get_vlan_info(), {"mode":"trunk","tag":[5,15]})
        self.assertEqual(bridge.find_port("p6").get_vlan_info(), {"mode":"trunk","tag":[6,16]})
        
        bridge.del_port("p1")
        bridge.del_port("p3")
        bridge.del_port("p5")
        self.assertEqual(len(bridge.get_ports()), 4)
        
        self.assertEqual(bridge.find_port("p0"), None)
        self.assertEqual(bridge.find_port("p1"), None)
        self.assertEqual(bridge.find_port("p2").get_name(), "p2")
        self.assertEqual(bridge.find_port("p3"), None)
        self.assertEqual(bridge.find_port("p4").get_name(), "p4")
        self.assertEqual(bridge.find_port("p5"), None)
        self.assertEqual(bridge.find_port("p6").get_name(), "p6")
        

    
    def init_ovs(self):
        cmd_del_all_bridge = "ovs-vsctl show | grep Bridge | awk '{print $2}' | xargs -n 1 ovs-vsctl del-br"
        subprocess.run(cmd_del_all_bridge, shell=True)
        
        #check bridge is not exist
        bridge = self.ovs.get_bridges()
        self.assertEqual(len(bridge), 0)

if __name__ == '__main__':
    unittest.main()

