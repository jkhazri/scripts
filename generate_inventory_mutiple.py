import os
import argparse

def generate_files(access_method, ip_addresses, usernames, ssh_password_storage_path, infra_groupname, ssh_key_storage_path, node_names):
    if len(ip_addresses) != len(usernames) or len(usernames) != len(node_names):
        print("ERROR: The number of IP addresses, usernames, and node names must be the same.")
        return

    hosts_path = "/etc/ansible/hosts"
    inventory_path = "/etc/ansible/inventory.xml"

    print(f"Generating files with:")
    print(f" Access Method: {access_method}")
    print(f" Infrastructure Group: {infra_groupname}")

    if access_method == "password":
        if not ssh_password_storage_path:
            print("ERROR: --ssh_password_storage_path is required for password authentication.")
            return
    elif access_method == "privatesshkey":
        if not ssh_key_storage_path:
            print("ERROR: --ssh_key_storage_path is required for private key authentication.")
            return
    else:
        print("ERROR: Invalid access method. Use 'password' or 'privatesshkey'.")
        return

    # Ensure /etc/ansible exists
    os.makedirs("/etc/ansible", exist_ok=True)

    try:
        # Generate inventory.xml content
        inventory_content = '<?xml version="1.0" ?>\n<project>\n'
        for ip, user, node in zip(ip_addresses, usernames, node_names):
            inventory_content += f'''  <node name="{node}"
        description="Server at {ip}"
        tags="linux, server"
        hostname="{ip}"
        osArch=""
        osFamily=""
        osName=""
        osVersion=""
        username="{user}"
        '''
            if access_method == "privatesshkey":
                inventory_content += f'''ssh-key-storage-path="{ssh_key_storage_path}"
        ssh-authentication="privateKey"'''
            elif access_method == "password":
                inventory_content += f'''ssh-password-storage-path="{ssh_password_storage_path}"
        ssh-authentication="password"'''
            
            inventory_content += " />\n"

        inventory_content += "</project>\n"

        # Write inventory.xml
        with open(inventory_path, "w") as inventory_file:
            inventory_file.write(inventory_content)

        # Read the hostname from the system
        container_hostname = os.uname()[1]

        # Generate hosts file content
        hosts_content = f"""[mylocal]
{container_hostname} ansible_host=localhost ansible_user=rundeck ansible_password=rundeck ansible_become_password=rundeck

[{infra_groupname}]
"""
        for ip, user, node in zip(ip_addresses, usernames, node_names):
            hosts_content += f"{node} ansible_host={ip} ansible_user={user}\n"

        # Write the hosts file
        with open(hosts_path, "w") as hosts_file:
            hosts_file.write(hosts_content)

        print(f"✅ Files successfully created:")
        print(f" - {inventory_path}")
        print(f" - {hosts_path}")
    except Exception as e:
        print(f"❌ Error writing files: {e}")

# Command-line argument handling
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate inventory and hosts files for multiple nodes.")
    parser.add_argument("--access_method", type=str, required=True, choices=["password", "privatesshkey"], help="Access method: 'password' or 'privatesshkey'")
    parser.add_argument("--ip_addresses", type=str, required=True, help="Comma-separated list of server IP addresses")
    parser.add_argument("--usernames", type=str, required=True, help="Comma-separated list of usernames for access")
    parser.add_argument("--ssh_password_storage_path", type=str, required=False, help="Path to SSH password storage file (required for password method)")
    parser.add_argument("--ssh_key_storage_path", type=str, required=False, help="Path to SSH private key storage file (required for privatesshkey method)")
    parser.add_argument("--infra_groupname", type=str, required=True, help="Infrastructure group name")
    parser.add_argument("--node_names", type=str, required=True, help="Comma-separated list of node names (hostnames)")
    args = parser.parse_args()

    # Split comma-separated strings into lists
    ip_addresses = args.ip_addresses.split(',')
    usernames = args.usernames.split(',')
    node_names = args.node_names.split(',')

    generate_files(
        access_method=args.access_method,
        ip_addresses=ip_addresses,
        usernames=usernames,
        ssh_password_storage_path=args.ssh_password_storage_path,
        infra_groupname=args.infra_groupname,
        ssh_key_storage_path=args.ssh_key_storage_path,
        node_names=node_names
    )
