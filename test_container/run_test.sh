#!/bin/bash

systemctl start openvswitch
ovs-vsctl set-manager ptcp:5678

cd /root/ovspy
git checkout develop
git pull
pip3 install -r requirements.txt
python3 -m xmlrunner --output-file /root/test_result.xml ovspy_test.py

