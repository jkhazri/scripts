#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, parse


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Ansible inventory and XML for Kubernetes clusters.")
    parser.add_argument('--access_method', required=True)
    parser.add_argument('--ssh_password_storage_path', default='')
    parser.add_argument('--ssh_key_storage_path', default='')

    parser.add_argument('--ip_addresses_K8S_Master', default='')
    parser.add_argument('--usernames_K8S_Master', default='')
    parser.add_argument('--node_names_K8S_Master', default='')
    parser.add_argument('--infra_groupname_K8S_Master', default='')

    parser.add_argument('--ip_addresses_K8S_Slave', default='')
    parser.add_argument('--usernames_K8S_Slave', default='')
    parser.add_argument('--node_names_K8S_Slave', default='')
    parser.add_argument('--infra_groupname_K8S_Slave', default='')

    return parser.parse_args()


def split_and_clean(arg):
    return [x.strip() for x in arg.split(',') if x.strip()]


def insert_into_group(existing_lines, group, new_entries):
    group_header = f"[{group}]"
    updated_lines = []
    inserted = False
    i = 0

    while i < len(existing_lines):
        line = existing_lines[i]
        updated_lines.append(line)
        if line.strip() == group_header:
            i += 1
            # Add new entries right after the group header or existing content
            while i < len(existing_lines) and not existing_lines[i].startswith('['):
                updated_lines.append(existing_lines[i])
                i += 1
            updated_lines.extend(new_entries)
            inserted = True
            continue
        i += 1

    if not inserted:
        updated_lines.append("")
        updated_lines.append(group_header)
        updated_lines.extend(new_entries)

    return updated_lines


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


def read_existing_ini(path):
    return path.read_text().splitlines() if path.exists() else []


def read_existing_xml(path):
    if path.exists():
        return parse(path).getroot()
    else:
        root = Element("project")
        SubElement(root, "node", {
            "name": "rundeck",
            "hostname": "localhost",
            "username": "rundeck",
            "ssh-password": "*******",
            "ssh-become-password": "********",
            "tags": "mylocal",
            "osFamily": "unix"
        })
        return root


def main():
    args = parse_args()

    # Paths
    hosts_path = Path("/etc/ansible/hosts")
    xml_path = Path("/etc/ansible/inventory.xml")

    existing_ini = read_existing_ini(hosts_path)
    final_ini = existing_ini[:]

    xml_root = read_existing_xml(xml_path)

    # MASTER
    if all([args.ip_addresses_K8S_Master, args.usernames_K8S_Master, args.node_names_K8S_Master, args.infra_groupname_K8S_Master]):
        master_ips = split_and_clean(args.ip_addresses_K8S_Master)
        master_users = split_and_clean(args.usernames_K8S_Master)
        master_nodes = split_and_clean(args.node_names_K8S_Master)
        if len(master_ips) == len(master_users) == len(master_nodes):
            master_entries = [
                f"{name} ansible_host={ip} ansible_user={user}"
                for name, ip, user in zip(master_nodes, master_ips, master_users)
            ]
            final_ini = insert_into_group(final_ini, args.infra_groupname_K8S_Master, master_entries)
            for name, ip, user in zip(master_nodes, master_ips, master_users):
                generate_xml_node(xml_root, name, ip, user, args.infra_groupname_K8S_Master, args.ssh_key_storage_path)
        else:
            print("Master node field count mismatch — skipping master section.")
    else:
        print("Incomplete master input — skipping master section.")

    # SLAVE
    if all([args.ip_addresses_K8S_Slave, args.usernames_K8S_Slave, args.node_names_K8S_Slave, args.infra_groupname_K8S_Slave]):
        slave_ips = split_and_clean(args.ip_addresses_K8S_Slave)
        slave_users = split_and_clean(args.usernames_K8S_Slave)
        slave_nodes = split_and_clean(args.node_names_K8S_Slave)
        if len(slave_ips) == len(slave_users) == len(slave_nodes):
            slave_entries = [
                f"{name} ansible_host={ip} ansible_user={user}"
                for name, ip, user in zip(slave_nodes, slave_ips, slave_users)
            ]
            final_ini = insert_into_group(final_ini, args.infra_groupname_K8S_Slave, slave_entries)
            for name, ip, user in zip(slave_nodes, slave_ips, slave_users):
                generate_xml_node(xml_root, name, ip, user, args.infra_groupname_K8S_Slave, args.ssh_key_storage_path)
        else:
            print("Slave node field count mismatch — skipping slave section.")
    else:
        print("Incomplete slave input — skipping slave section.")

    # WRITE FILES
    hosts_path.write_text('\n'.join(final_ini) + '\n')
    ElementTree(xml_root).write(xml_path, encoding="utf-8", xml_declaration=True)

    print("Inventory files generated:")
    print(f"  INI:  {hosts_path}")
    print(f"  XML:  {xml_path}")


if __name__ == "__main__":
    main()
