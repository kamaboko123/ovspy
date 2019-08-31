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
        
        #add_port
        
        #trunk
        bridge.add_port("p1")
        self.assertEqual(len(bridge.get_ports()), 2)
        
        bridge.add_port("p2")
        self.assertEqual(len(bridge.get_ports()), 3)
        
        for p in bridge.get_ports():
            print(p.get_name())
    
    def init_ovs(self):
        cmd_del_all_bridge = "ovs-vsctl show | grep Bridge | awk '{print $2}' | xargs -n 1 ovs-vsctl del-br"
        subprocess.run(cmd_del_all_bridge, shell=True)
        
        #check bridge is not exist
        bridge = self.ovs.get_bridges()
        self.assertEqual(len(bridge), 0)

if __name__ == '__main__':
    unittest.main()

