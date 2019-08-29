import unittest
import subprocess
from ovspy.client import OvsClient


class TestOvspy(unittest.TestCase):
    def setUp(self):
        cmd_del_all_bridge = "sudo ovs-vsctl show | grep Bridge | awk '{print $2}' | xargs -n 1 sudo ovs-vsctl del-br"
        subprocess.run(cmd_del_all_bridge, shell=True)
        self.ovs = OvsClient(5678)
    
    def test_bridge(self):
        bridge = self.ovs.get_bridge()
        self.assertEqual(len(bridge), 0)

if __name__ == '__main__':
    unittest.main()

