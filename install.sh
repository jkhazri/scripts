#!/bin/bash

# Create log directory
sudo mkdir -p /var/log/sshlog
sudo chmod 755 /var/log/sshlog

# Create configuration directory
sudo mkdir -p /etc/sshlog/conf.d
sudo chmod 755 /etc/sshlog

# Create local entrypoint script
sudo tee /etc/sshlog/entrypoint.sh > /dev/null <<'EOF'
#!/bin/sh
rm -rf /etc/sshlog/conf.d/*
mkdir -p /etc/sshlog/conf.d

cat <<YAML > /etc/sshlog/conf.d/sshlog.yaml
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
YAML

EOF

# Make sure it's executable
sudo chmod +x /etc/sshlog/entrypoint.sh

echo "creation of directory done!!"

# Install Docker
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
echo "install docker is done!!"

# Run container with external entrypoint
docker run -d --restart=always --name sshlog \
  --privileged \
  -v /sys:/sys:ro \
  -v /dev:/dev \
  -v /proc:/proc \
  -v /etc/passwd:/etc/passwd:ro \
  -v /var/log/sshlog:/var/log/sshlog \
  -v /etc/sshlog:/etc/sshlog \
  --pid=host \
  sshlog/agent:latest

# Restart the container
docker restart sshlog
