import unittest
import subprocess
from ovspy.client import OvsClient
from ovspy import ovspy_error

class TestOvspy(unittest.TestCase):
    def setUp(self):
        self.ovs = OvsClient(5678)
        self.ovs.SEND_DEBUG = False
        self.ovs.RECV_DEBUG = False
        
    def test_bridge(self):
        self.init_ovs()
        
        #check empty
        bridges = self.ovs.get_bridges()
        self.assertEqual(len(bridges), 0)
        
        self.ovs.add_bridge("br1")
        self.ovs.add_bridge("br2")
        self.assertEqual(len(self.ovs.get_bridges()), 2)
        
        self.assertEqual(self.ovs.find_bridge("br0"), None)
        self.assertEqual(self.ovs.find_bridge("br1").get_name(), "br1")
        self.assertEqual(self.ovs.find_bridge("br2").get_name(), "br2")
        
        with self.assertRaises(ovspy_error.Duplicate):
            self.ovs.add_bridge("br1")
        
        self.ovs.del_bridge("br1")
        self.assertEqual(self.ovs.find_bridge("br1"), None)
        
        self.assertEqual(len(self.ovs.get_bridges()), 1)
        
        with self.assertRaises(ovspy_error.NotFound):
            self.ovs.del_bridge("br1")
        self.assertEqual(len(self.ovs.get_bridges()), 1)
        
        self.assertEqual(self.ovs.get_bridges()[0].get_name(), "br2")
    
    def test_ports(self):
        self.init_ovs()
        
        bridge_name = "br0"
        self.ovs.add_bridge("br0")
        #cmd_del_all_bridge = "ovs-vsctl add-br %s" % bridge_name
        #subprocess.run(cmd_del_all_bridge, shell=True)
        
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
        
        with self.assertRaises(ValueError):
            bridge.add_port("p7", "test")
        
        with self.assertRaises(ValueError):
            bridge.add_port("p8", {})
        
        with self.assertRaises(ovspy_error.Duplicate):
            bridge.add_port("p1")
        
        bridge.add_port("p9", 10, port_type="internal")
        
        self.assertEqual(len(bridge.get_ports()), 8)
        
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
        self.assertEqual(bridge.find_port("p9").get_vlan_info(), {"mode":"access", "tag":10})
        
        self.assertEqual(bridge.find_port("p1").is_internal(), False)
        self.assertEqual(bridge.find_port("p3").is_internal(), False)
        self.assertEqual(bridge.find_port("p9").is_internal(), True)
        
        bridge.del_port("p1")
        bridge.del_port("p3")
        bridge.del_port("p5")
        self.assertEqual(len(bridge.get_ports()), 5)
        
        self.assertEqual(bridge.find_port("p0"), None)
        self.assertEqual(bridge.find_port("p1"), None)
        self.assertEqual(bridge.find_port("p2").get_name(), "p2")
        self.assertEqual(bridge.find_port("p3"), None)
        self.assertEqual(bridge.find_port("p4").get_name(), "p4")
        self.assertEqual(bridge.find_port("p5"), None)
        self.assertEqual(bridge.find_port("p6").get_name(), "p6")
        
        with self.assertRaises(ovspy_error.NotFound):
            bridge.del_port("p0")
        
        self.assertEqual(len(bridge.get_ports()), 5)
    
    def init_ovs(self):
        #cmd_del_all_bridge = "sudo ovs-vsctl show | grep Bridge | awk '{print $2}' | xargs -n 1 ovs-vsctl del-br"
        #subprocess.run(cmd_del_all_bridge, shell=True)
        for br in self.ovs.get_bridges():
            self.ovs.del_bridge(br.get_name())
        
        #check bridge is not exist
        bridge = self.ovs.get_bridges()
        self.assertEqual(len(bridge), 0)

if __name__ == '__main__':
    unittest.main()

