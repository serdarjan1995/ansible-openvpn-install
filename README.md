# vpnAutomation 
### Install Ansible: 
For Ubuntu: 
```
$ sudo apt update
$ sudo apt install software-properties-common
$ sudo apt-add-repository --yes --update ppa:ansible/ansible
$ sudo apt install ansible
```
Reference 
https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html

#### !NOTE:  
Default `python` on your machine should be `python3` (python=python3)  
`pexpect` module also should be installed; if not `pip3 install pexpect`  

### Running:
Clone this repo and `cd` into repo directory.  
First of all write your machine IP's to `hosts` file.  
Your machines should be configured to ssh via public/private certificate.  
In case of username/password login add `--ask-pass` argument to the end of the commands.  
#### ! You should run ansible commands via `root` user  
```
root@machine:/# ansible all -m ping -u azureuser
213.199.129.50 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
156.11.45.178 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

Start the automation 
```
root@machine:/# ansible-playbook site.yml -u azureuser

PLAY [servers] ***************************************************************************************

TASK [Gathering Facts] *******************************************************************************
ok: [213.199.129.50]
ok: [156.11.45.178]
...
```
