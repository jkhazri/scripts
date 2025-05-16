import os
import argparse
import traceback

def generate_files(access_method, ip_addresses, usernames, ssh_password_storage_path,
                   infra_groupname, ssh_key_storage_path, node_names):
    if len(ip_addresses) != len(usernames) or len(usernames) != len(node_names):
        print("ERROR: The number of IP addresses, usernames, and node names must be the same.")
        return

    hosts_path = "/etc/ansible/hosts"
    inventory_path = "/etc/ansible/inventory.xml"

    print(f"Generating files with:")
    print(f" Access Method: {access_method}")
    print(f" Infrastructure Group: {infra_groupname}")

    # Allow empty fields to pass
    if access_method == "password":
        if ssh_password_storage_path is None:
            ssh_password_storage_path = ""
    elif access_method == "privatesshkey":
        if ssh_key_storage_path is None:
            ssh_key_storage_path = ""
    else:
        print("ERROR: Invalid access method. Use 'password' or 'privatesshkey'.")
        return

    os.makedirs("/etc/ansible", exist_ok=True)

    try:
        # === Handle inventory.xml ===
        if os.path.exists(inventory_path):
            with open(inventory_path, "r") as f:
                content = f.read()
            if "</project>" in content:
                content = content.replace("</project>", "")  # Remove closing tag to insert nodes
        else:
            content = '<?xml version="1.0" ?>\n<project>\n'

        for ip, user, node in zip(ip_addresses, usernames, node_names):
            if f'name="{node}"' not in content:
                content += f'''  <node name="{node}"
        description="Server at {ip}"
        tags="linux, server"
        hostname="{ip}"
        osArch=""
        osFamily=""
        osName=""
        osVersion=""
        username="{user}"\n'''
                if access_method == "privatesshkey":
                    content += f'''        ssh-key-storage-path="{ssh_key_storage_path}"\n        ssh-authentication="privateKey"'''
                elif access_method == "password":
                    content += f'''        ssh-password-storage-path="{ssh_password_storage_path}"\n        ssh-authentication="password"'''
                content += " />\n"

        content += "</project>\n"

        with open(inventory_path, "w") as f:
            f.write(content)

        # === Handle /etc/ansible/hosts ===
        container_hostname = os.uname()[1]
        if os.path.exists(hosts_path):
            with open(hosts_path, "r") as f:
                existing_hosts = f.read()
        else:
            existing_hosts = ""

        hosts_lines = []

        # Write [mylocal] once
        if "[mylocal]" not in existing_hosts:
            hosts_lines.append(f"[mylocal]\n{container_hostname} ansible_host=localhost ansible_user=rundeck ansible_password=rundeck ansible_become_password=rundeck\n")

        # Add or append group section
        group_section_header = f"\n[{infra_groupname}]\n"
        if f"[{infra_groupname}]" not in existing_hosts:
            hosts_lines.append(group_section_header)

        for ip, user, node in zip(ip_addresses, usernames, node_names):
            entry = f"{node} ansible_host={ip} ansible_user={user}"
            if entry not in existing_hosts:
                hosts_lines.append(f"{entry}\n")

        with open(hosts_path, "a") as f:
            f.writelines(hosts_lines)

        print(f"✅ Files successfully updated or created:")
        print(f" - {inventory_path}")
        print(f" - {hosts_path}")
    except Exception as e:
        print("❌ Error writing files:")
        traceback.print_exc()

# === CLI Argument Parser ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate inventory and hosts files for multiple nodes.")
    parser.add_argument("--access_method", type=str, required=True, choices=["password", "privatesshkey"],
                        help="Access method: 'password' or 'privatesshkey'")
    parser.add_argument("--ip_addresses", type=str, required=True, help="Comma-separated list of server IP addresses")
    parser.add_argument("--usernames", type=str, required=True, help="Comma-separated list of usernames for access")
    parser.add_argument("--ssh_password_storage_path", type=str, required=False,
                        help="Path to SSH password storage file (required for password method)")
    parser.add_argument("--ssh_key_storage_path", type=str, required=False,
                        help="Path to SSH private key storage file (required for privatesshkey method)")
    parser.add_argument("--infra_groupname", type=str, required=True, help="Infrastructure group name")
    parser.add_argument("--node_names", type=str, required=True, help="Comma-separated list of node names (hostnames)")
    args = parser.parse_args()

# Split and sanitize input
ip_addresses = [ip.strip() for ip in args.ip_addresses.split(',') if ip.strip()]
usernames = [u.strip() for u in args.usernames.split(',') if u.strip()]
node_names = [n.strip() for n in args.node_names.split(',') if n.strip()]

# Skip if any part of node data is missing
if not ip_addresses or not usernames or not node_names:
    print("⚠️ Skipping update: no valid node data provided.")
    exit(0)

generate_files(
    access_method=args.access_method,
    ip_addresses=ip_addresses,
    usernames=usernames,
    ssh_password_storage_path=args.ssh_password_storage_path,
    infra_groupname=args.infra_groupname,
    ssh_key_storage_path=args.ssh_key_storage_path,
    node_names=node_names
)
