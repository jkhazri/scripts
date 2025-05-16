# scripts

## generate_inventory_mutiple.py is the script to generate MVMnodes
sudo python3 generate_inventory_mutiple.py     --access_method "privatesshkey"     --ip_addresses "192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4,192.168.1.5"     --usernames "user1,user2,user3,user4,user5"     --infra_groupname MvmNode     --ssh_password_storage_path ""     --ssh_key_storage_path key/hobohobo     --node_names "node-11,node-22,node-33,node-44,node-55"


## generate_inventory_Patch.py is the script that addsa  new Ansible script named impacted_server

python3 generate_inventory_Patch.py \
--access_method password \
--ip_addresses "192.168.1.3,192.168.1.5" \
--usernames "userFORD,userTESLA" \
--ssh_password_storage_path key/hobohobo \
--infra_groupname impacted_server \
--node_names "node-33,node-55"



  ## generate_inventory_Kube.py is the script that will generate the groups to manage K8s (both k8s-worker-data-plane && k8s-master-data-plane )
  

sudo python3 generate_inventory_Kube.py --access_method "privatesshkey" --ip_addresses_K8S_Master "192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4,192.168.1.5" --usernames_K8S_Master "user1,user2,user3,user4,user5" --infra_groupname_K8S_Master k8s-master-data-plane --ssh_password_storage_path "" --ssh_key_storage_path key/hobohobo --node_names_K8S_Master "node-11,node-22,node-33,node-44,node-55" --ip_addresses_K8S_Slave "192.0.1.1,192.0.1.2,192.0.1.3,192.0.1.4,192.0.1.5" --usernames_K8S_Slave "R1,R2,R3,R4,R5" --infra_groupname_K8S_Slave k8s-worker-data-plane --node_names_K8S_Slave "node-01,node-02,node-03,node-04,node-05"
