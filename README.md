## Requirements
Ansible >= 2.7
export WORKSPACE=/some/path

###Usage
- create ssh-key and add it to authorized_keys
- Setup the vms
		ansible-playbook bootstrap.yml
- install openshift and openstack
		ansible-playbook deploy-stacks.yml

