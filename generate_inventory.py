import os
import argparse

def generate_files(access_method, ip_address, username, ssh_password_storage_path, infra_groupname, ssh_key_storage_path, node_name):
    ansible_user = username  # Ensure ansible_user reflects the given username
    hosts_path = "/etc/ansible/hosts"
    inventory_path = "/etc/ansible/inventory.xml"
    
    print(f"Generating files with:")
    print(f"  Access Method: {access_method}")
    print(f"  IP Address: {ip_address}")
    print(f"  Username: {username}")
    print(f"  Infrastructure Group: {infra_groupname}")
    print(f"  Node Name: {node_name}")
    
    if access_method == "password":
        if not ssh_password_storage_path:
            print("ERROR: --ssh_password_storage_path is required for password authentication.")
            return
        
        inventory_content = f'''<?xml version="1.0" ?>
<project>
  <node name="{node_name}" description="Server at {ip_address}" tags="linux, server" hostname="{ip_address}" osArch="" osFamily="" osName="" osVersion="" username="{ansible_user}" ssh-password-storage-path="{ssh_password_storage_path}" ssh-authentication="password"/>
</project>
'''
    
    elif access_method == "privatesshkey":
        if not ssh_key_storage_path:
            print("ERROR: --ssh_key_storage_path is required for private key authentication.")
            return

        inventory_content = f'''<?xml version="1.0" ?>
<project>
  <node name="{node_name}" description="Server at {ip_address}" tags="linux, server" hostname="{ip_address}" osArch="" osFamily="" osName="" osVersion="" username="{ansible_user}" ssh-key-storage-path="{ssh_key_storage_path}" ssh-authentication="privateKey"/>
</project>
'''
    else:
        print("ERROR: Invalid access method. Use 'password' or 'privatesshkey'.")
        return
    
    # Ensure /etc/ansible exists
    os.makedirs("/etc/ansible", exist_ok=True)
    
    try:
        # Write inventory.xml
        with open(inventory_path, "w") as inventory_file:
            inventory_file.write(inventory_content)
        
        # Read the hostname from the system
        container_hostname = os.uname()[1]
        
        # Write the new hosts file with the required format
        hosts_content = f"""[mylocal]\n{container_hostname} ansible_host=localhost ansible_user=rundeck ansible_password=rundeck ansible_become_password=rundeck\n\n[MvmNode]\n{node_name} ansible_host={ip_address} ansible_user={ansible_user}\n"""
        
        with open(hosts_path, "w") as hosts_file:
            hosts_file.write(hosts_content)
        
        print(f"✅ Files successfully created:")
        print(f"  - {inventory_path}")
        print(f"  - {hosts_path}")

    except Exception as e:
        print(f"❌ Error writing files: {e}")

# Command-line argument handling
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate inventory and hosts files.")
    
    parser.add_argument("--access_method", type=str, required=True, choices=["password", "privatesshkey"], help="Access method: 'password' or 'privatesshkey'")
    parser.add_argument("--ip_address", type=str, required=True, help="Server IP address")
    parser.add_argument("--username", type=str, required=True, help="Username for access")
    parser.add_argument("--ssh_password_storage_path", type=str, required=False, help="Path to SSH password storage file (required for password method)")
    parser.add_argument("--ssh_key_storage_path", type=str, required=False, help="Path to SSH private key storage file (required for privatesshkey method)")
    parser.add_argument("--infra_groupname", type=str, required=True, help="Infrastructure group name")
    parser.add_argument("--node_name", type=str, required=True, help="Node name (hostname)")
    
    args = parser.parse_args()
    
    generate_files(
        access_method=args.access_method,
        ip_address=args.ip_address,
        username=args.username,
        ssh_password_storage_path=args.ssh_password_storage_path,
        infra_groupname=args.infra_groupname,
        ssh_key_storage_path=args.ssh_key_storage_path,
        node_name=args.node_name
    )
