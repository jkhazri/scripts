#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate Ansible inventory and XML for Kubernetes clusters."
    )

    parser.add_argument('--access_method', required=True, help='Access method (e.g., privatesshkey)')
    parser.add_argument('--ssh_password_storage_path', default='', help='SSH password path')
    parser.add_argument('--ssh_key_storage_path', default='', help='SSH private key path')

    parser.add_argument('--ip_addresses_K8S_Master', required=True)
    parser.add_argument('--usernames_K8S_Master', required=True)
    parser.add_argument('--node_names_K8S_Master', required=True)
    parser.add_argument('--infra_groupname_K8S_Master', required=True)

    parser.add_argument('--ip_addresses_K8S_Slave', default='')
    parser.add_argument('--usernames_K8S_Slave', default='')
    parser.add_argument('--node_names_K8S_Slave', default='')
    parser.add_argument('--infra_groupname_K8S_Slave', default='')

    return parser.parse_args()

def split_and_validate(arg_str, expected_len, arg_name):
    items = [item.strip() for item in arg_str.split(',') if item.strip()]
    if len(items) != expected_len:
        print(f"Error: '{arg_name}' expects {expected_len} items, but got {len(items)}.")
        sys.exit(1)
    return items

def generate_inventory_section(group_name, node_names, ips, users):
    lines = [f"[{group_name}]"]
    for name, ip, user in zip(node_names, ips, users):
        lines.append(f"{name} ansible_host={ip} ansible_user={user}")
    return lines

def generate_xml_node(parent, name, ip, user, tag, ssh_key_path=None):
    node = SubElement(parent, "node", {
        "name": name,
        "hostname": ip,
        "username": user,
        "tags": tag,
        "osFamily": "unix"
    })

    if ssh_key_path:
        node.set("ssh-keypath", ssh_key_path)

def main():
    args = parse_args()

    # MASTER
    master_ips = [ip.strip() for ip in args.ip_addresses_K8S_Master.split(',') if ip.strip()]
    master_users = split_and_validate(args.usernames_K8S_Master, len(master_ips), 'usernames_K8S_Master')
    master_nodes = split_and_validate(args.node_names_K8S_Master, len(master_ips), 'node_names_K8S_Master')

    # SLAVE (conditionally parse)
    slave_nodes = slave_ips = slave_users = []
    include_slaves = all([args.ip_addresses_K8S_Slave.strip(), args.usernames_K8S_Slave.strip(), args.node_names_K8S_Slave.strip()])

    if include_slaves:
        slave_ips = [ip.strip() for ip in args.ip_addresses_K8S_Slave.split(',') if ip.strip()]
        slave_users = split_and_validate(args.usernames_K8S_Slave, len(slave_ips), 'usernames_K8S_Slave')
        slave_nodes = split_and_validate(args.node_names_K8S_Slave, len(slave_ips), 'node_names_K8S_Slave')

    # --------- INI GENERATION ---------
    ini_lines = []

    ini_lines.append("[mylocal]")
    ini_lines.append("rundeck ansible_host=localhost ansible_user=rundeck ansible_password=rundeck ansible_become_password=rundeck")
    ini_lines.append("")

    ini_lines += generate_inventory_section(args.infra_groupname_K8S_Master, master_nodes, master_ips, master_users)
    ini_lines.append("")

    if include_slaves:
        ini_lines += generate_inventory_section(args.infra_groupname_K8S_Slave, slave_nodes, slave_ips, slave_users)
        ini_lines.append("")
    else:
        print("No Slave nodes defined, skipping Slave inventory.")

    # Write INI to /etc/ansible/hosts
    hosts_path = Path("/etc/ansible/hosts")
    hosts_path.write_text('\n'.join(ini_lines))

    # --------- XML GENERATION ---------
    project = Element("project")

    # Localhost
    SubElement(project, "node", {
        "name": "rundeck",
        "hostname": "localhost",
        "username": "rundeck",
        "ssh-password": "*******",
        "ssh-become-password": "********",
        "tags": "mylocal",
        "osFamily": "unix"
    })

    # Master Nodes
    for name, ip, user in zip(master_nodes, master_ips, master_users):
        generate_xml_node(project, name, ip, user, args.infra_groupname_K8S_Master, args.ssh_key_storage_path)

    # Slave Nodes
    if include_slaves:
        for name, ip, user in zip(slave_nodes, slave_ips, slave_users):
            generate_xml_node(project, name, ip, user, args.infra_groupname_K8S_Slave, args.ssh_key_storage_path)

    # Write XML to /etc/ansible/inventory.xml
    inventory_xml_path = Path("/etc/ansible/inventory.xml")
    ElementTree(project).write(inventory_xml_path, encoding="utf-8", xml_declaration=True)

    print(f"Inventory files generated:")
    print(f"  INI:  {hosts_path}")
    print(f"  XML:  {inventory_xml_path}")

if __name__ == "__main__":
    main()
