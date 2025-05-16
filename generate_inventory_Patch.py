import os
import argparse

def generate_files(access_method, ip_addresses, usernames, ssh_password_storage_path,
                   infra_groupname, ssh_key_storage_path, node_names):
    hosts_path = "/etc/ansible/hosts"
    inventory_path = "/etc/ansible/inventory.xml"

    # Check if both files exist
    if not os.path.exists(hosts_path):
        print(f"❌ ERROR: {hosts_path} does not exist.")
        return
    if not os.path.exists(inventory_path):
        print(f"❌ ERROR: {inventory_path} does not exist.")
        return

    # Check lists match in length
    if not (len(ip_addresses) == len(usernames) == len(node_names)):
        print("❌ ERROR: The number of IP addresses, usernames, and node names must be the same.")
        return

    # Read current hosts file content
    try:
        with open(hosts_path, "r") as f:
            existing_lines = f.readlines()
    except Exception as e:
        print(f"❌ Failed to read {hosts_path}: {e}")
        return

    # Prepare for insertion
    group_header = f"[{infra_groupname}]"
    new_hosts_lines = []
    in_target_group = False
    group_found = False
    added_nodes = set(node_names)

    for line in existing_lines:
        stripped = line.strip()

        if stripped.startswith('[') and stripped.endswith(']'):
            in_target_group = (stripped == group_header)
            if in_target_group:
                group_found = True
            new_hosts_lines.append(line)
            continue

        if in_target_group:
            node_name = line.strip().split()[0] if line.strip() else ''
            if node_name in added_nodes:
                continue  # Avoid duplicate entries

        new_hosts_lines.append(line)

    # If group does not exist, add it at the end
    if not group_found:
        new_hosts_lines.append(f"\n{group_header}\n")

    # Append new entries
    for ip, user, node in zip(ip_addresses, usernames, node_names):
        new_hosts_lines.append(f"{node} ansible_host={ip} ansible_user={user}\n")

    # Write back updated hosts file
    try:
        with open(hosts_path, "w") as f:
            f.writelines(new_hosts_lines)
        print(f"✅ Successfully updated {hosts_path} under group [{infra_groupname}]")
    except Exception as e:
        print(f"❌ Failed to write to {hosts_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Append nodes to an existing Ansible hosts file under a specific group.")
    parser.add_argument("--access_method", type=str, required=True, choices=["password", "privatesshkey"], help="Access method: 'password' or 'privatesshkey'")
    parser.add_argument("--ip_addresses", type=str, required=True, help="Comma-separated list of server IP addresses")
    parser.add_argument("--usernames", type=str, required=True, help="Comma-separated list of usernames for access")
    parser.add_argument("--ssh_password_storage_path", type=str, required=False, help="Path to SSH password storage file (required for password method)")
    parser.add_argument("--ssh_key_storage_path", type=str, required=False, help="Path to SSH private key storage file (required for privatesshkey method)")
    parser.add_argument("--infra_groupname", type=str, required=True, help="Infrastructure group name to append entries to")
    parser.add_argument("--node_names", type=str, required=True, help="Comma-separated list of node names (hostnames)")

    args = parser.parse_args()

    # Validate access method requirements
    if args.access_method == "password" and not args.ssh_password_storage_path:
        print("❌ ERROR: --ssh_password_storage_path is required for password access method.")
        exit(1)
    if args.access_method == "privatesshkey" and not args.ssh_key_storage_path:
        print("❌ ERROR: --ssh_key_storage_path is required for privatesshkey access method.")
        exit(1)

    # Parse input lists
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
