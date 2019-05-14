## Requirements
Ansible >= 2.7
export WORKSPACE=/some/path

## Usage
- create ssh-key and add it to authorized_keys
- Setup the vms

	ansible-playbook bootstrap.yml
- install openshift and openstack, create fake nodes

	ansible-playbook deploy-stacks.yml

## Design
Design document is at
https://docs.google.com/document/d/1Oa69nVeP6h0nPJaaDJfx7w9PfrCRFeT7jbNKiI0H7Us/edit?ts=5cd04ed1#heading=h.ab3472z6co0i

We are using fake compute node image created by
Mike Bayer (with minor changes) https://github.com/zzzeek/overcloud_basic
Thanks Mike.

