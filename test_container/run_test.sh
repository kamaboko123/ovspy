#!/bin/bash

systemctl start openvswitch
ovs-vsctl set-manager ptcp:5678

cd /root/ovspy
git checkout develop
git pull
python3 ovspy_test.py

