# scripts

sudo python3 generate_inventory_mutiple.py     --access_method "privatesshkey"     --ip_addresses "192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4,192.168.1.5"     --usernames "user1,user2,user3,user4,user5"     --infra_groupname MvmNode     --ssh_password_storage_path ""     --ssh_key_storage_path key/hobohobo     --node_names "node-11,node-22,node-33,node-44,node-55"


patch python generation
python3 generate_inventory_Patch.py \
  --access_method=password \
  --ip_addresses=185.211.155.245,185.211.155.247,185.211.155.240 \
  --usernames=onecloud,admin,jakob \
  --node_names=node_jaber,node_admin,node_psql \
  --node_ids=245,247,24 \
  --ssh_password_storage_path=keys/password \
  --infra_groupname=impacted_server
