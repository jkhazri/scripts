#!/bin/bash

# Source os-release for distro info
if [ -f /etc/os-release ]; then
    . /etc/os-release
else
    echo "Cannot detect OS."
    exit 1
fi

# Track if we should generate sshlog.yaml or not
GENERATE_CONFIG=true

# Check distro family
if [[ "$ID_LIKE" == *"debian"* ]]; then

    echo "Detected Debian-based system ($ID)"
    wget https://github.com/sshlog/agent/releases/download/v1.0.0/sshlog_1.0.0_amd64.deb
    dpkg -i sshlog_1.0.0_amd64.deb

elif [[ "$ID_LIKE" == *"rhel"* || "$ID_LIKE" == *"centos"* || "$ID_LIKE" == *"fedora"* ]]; then

    if [[ "$VERSION_ID" =~ ^8 ]]; then
        echo "Detected RHEL-like system version 8.x ($ID $VERSION_ID)"
        curl https://raw.githubusercontent.com/jkhazri/scripts/refs/heads/main/install-sshlog-forRHELV8.sh | sh
        GENERATE_CONFIG=false

    elif [[ "$VERSION_ID" =~ ^9 ]]; then
        echo "Detected RHEL-like system version 9.x ($ID $VERSION_ID)"
        yum install -y wget
        wget https://github.com/sshlog/agent/releases/download/v1.0.0/sshlog-1.0-0.x86_64.rpm
        sudo yum install sshlog-1.0-0.x86_64.rpm -y

    else
        echo "Unsupported RHEL-like version: $VERSION_ID"
        exit 1
    fi

else
    echo "Unsupported or unknown distro family: ID=$ID, ID_LIKE=$ID_LIKE, VERSION_ID=$VERSION_ID"
    exit 1
fi

# Only proceed with sshlog.yaml setup if not on version 8
if [ "$GENERATE_CONFIG" = true ]; then
    # Remove all files under /etc/sshlog/conf.d/
    rm -f /etc/sshlog/conf.d/*

    # Create sshlog.yaml with correct YAML formatting
    cat << 'EOF' > /etc/sshlog/conf.d/sshlog.yaml
# Description:
# Logs all events (e.g., login, command start, file upload) to a single file

events:
  - event: log_general_activity
    triggers:
      - connection_established
      #- connection_auth_failed
      - connection_close
      - command_start
      - command_finish
      - file_upload
    #filters:
      #ignore_existing_logins: True
    actions:
      - action: log_events
        plugin: eventlogfile_action
        log_file_path: /var/log/sshlog/event.log
        max_size_mb: 10
        number_of_log_files: 5
        output_json: True
EOF

    echo "sshlog.yaml created at /etc/sshlog/conf.d/sshlog.yaml"
fi
