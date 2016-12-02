Setup SSH key on Ansible Host
Add user "ansible" on managed host

ssh-copy-id -i ~/.ssh/id_rsa.pub [managed_host_ip]
ansible all -i hosts -a "ls -al \/ "
