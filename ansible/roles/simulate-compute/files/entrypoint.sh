#!/bin/bash

set -x
DEVICE=eth0
MY_MACADDR=$( ip addr show ${DEVICE} | grep -Po 'link/ether \K[\da-f:]+'  )
MY_IP=$( ip addr show ${DEVICE} | grep -Po 'inet \K[\d.]+'  )
MY_HOSTNAME=$( cat /etc/hostname )

WRITE_CONF="/write_config.py -e container_ip=${MY_IP} -e container_hostname=${MY_HOSTNAME}"

if [ ! -f /etc/hosts.docker ]; then
    cp /etc/hosts /etc/hosts.docker
fi

cp /etc/hosts.docker /etc/hosts
cat /hosts >> /etc/hosts

# patch fake virt driver script into nova installation location
NOVA_VIRT_PATH=$( python -c "import os; from nova import virt; print(os.path.dirname(virt.__file__))" )
cp /fake_vif.py ${NOVA_VIRT_PATH}/



pushd /etc/nova
${WRITE_CONF} nova.conf.fragment /nova.conf nova.conf
popd

pushd /etc/neutron
${WRITE_CONF} neutron.conf.fragment /neutron.conf neutron.conf
${WRITE_CONF} openvswitch_agent.ini.fragment /openvswitch_agent.ini plugins/ml2/openvswitch_agent.ini
popd

# OVS:
mkdir /var/run/openvswitch
chown openvswitch:hugetlbfs /var/run/openvswitch/
sudo -u openvswitch ovsdb-tool create
ovsdb-server /etc/openvswitch/conf.db -vconsole:emer -vsyslog:err -vfile:info --remote "ptcp:6640:127.0.0.1" --remote=punix:/var/run/openvswitch/db.sock --private-key=db:Open_vSwitch,SSL,private_key --certificate=db:Open_vSwitch,SSL,certificate --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert --user openvswitch:hugetlbfs --no-chdir --log-file=/var/log/openvswitch/ovsdb-server.log --pidfile=/var/run/openvswitch/ovsdb-server.pid --detach
# ovs-vsctl set-manager "ptcp:6640:127.0.0.1"
ovs-vswitchd unix:/var/run/openvswitch/db.sock -vconsole:emer -vsyslog:err -vfile:info --mlockall --user openvswitch:hugetlbfs --no-chdir --log-file=/var/log/openvswitch/ovs-vswitchd.log --pidfile=/var/run/openvswitch/ovs-vswitchd.pid --detach

# TODO: ip address on the bridge?
ovs-vsctl -t 10 -- --may-exist add-br br-ex -- set bridge br-ex other-config:hwaddr=${MY_MACADDR} -- set bridge br-ex fail_mode=standalone -- del-controller br-ex


nova-compute &
/usr/bin/python2 /usr/bin/neutron-openvswitch-agent --config-file /usr/share/neutron/neutron-dist.conf --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/openvswitch_agent.ini --config-dir /etc/neutron/conf.d/common --log-file=/var/log/neutron/openvswitch-agent.log  &

while [ 1 ] ; do
  sleep 1
done


