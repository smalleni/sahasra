FROM centos

ARG delorean_url
ARG delorean_deps_url


RUN \
	yum install -y tcpdump iproute net-tools

RUN \
	cd /etc/yum.repos.d/ && \
	curl -O ${delorean_url} && \
    curl -O ${delorean_deps_url}

RUN \
   yum install -y openstack-nova-compute openstack-nova-migration openstack-neutron-ml2 openstack-neutron-openvswitch openstack-neutron-fwaas openstack-neutron

# copy partial conf files to their /etc/ locations.  the write_config.py
# script uses these to merge into a real conf file.
COPY ./nova.conf.fragment /etc/nova/
COPY ./neutron.conf.fragment /etc/neutron/
COPY ./openvswitch_agent.ini.fragment /etc/neutron/

# etc


VOLUME /etc/nova/original
VOLUME /etc/neutron/original

# we want to mount /etc/hosts_compute as a file
# VOLUME /etc/hosts_compute

COPY ./fake_vif.py /fake_vif.py
COPY ./write_config.py /write_config.py
COPY ./entrypoint.sh /entrypoint.sh

RUN \
	chmod 0755 /write_config.py /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

