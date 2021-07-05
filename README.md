# Ansible Callback Plugin 'opentelemetry'

## Requirements

```shell
sudo apk add g++

pip install opentelemetry-api
pip install opentelemetry-sdk
pip install opentelemetry-exporter-jaeger
```


Everytime we use the same playbook and the same inventory.

https://docs.ansible.com/ansible/latest/user_guide/playbooks_strategies.html

```
ansible-playbook -i inventory.ini playbook.yml
```
