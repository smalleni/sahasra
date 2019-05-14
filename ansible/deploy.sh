ansible-playbook -vvv bootstrap.yml 2>&1 | tee bootstrap.log
ansible-playbook -vvv -i hosts deploy-stacks.yml 2>&1 | tee deploy_stacks.log
