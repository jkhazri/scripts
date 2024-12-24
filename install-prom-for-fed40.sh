#!/bin/bash

# Install required packages
dnf install -y curl wget

# Download Prometheus tarball
mkdir -p /home/onecloud
wget -P /home/onecloud https://github.com/prometheus/prometheus/releases/download/v2.44.0/prometheus-2.44.0.linux-amd64.tar.gz

# Extract the tarball
tar -xvf /home/onecloud/prometheus-2.44.0.linux-amd64.tar.gz -C /home/onecloud
mv /home/onecloud/prometheus-2.44.0.linux-amd64 /home/onecloud/prometheus-files

# Create Prometheus user
useradd --no-create-home --shell /bin/false prometheus

# Create necessary directories
mkdir -p /etc/prometheus
mkdir -p /var/lib/prometheus
chown prometheus:prometheus /etc/prometheus
chown prometheus:prometheus /var/lib/prometheus

# Move binaries to /usr/local/bin
cp /home/onecloud/prometheus-files/prometheus /usr/local/bin/
cp /home/onecloud/prometheus-files/promtool /usr/local/bin/

# Set ownership for binaries
chown prometheus:prometheus /usr/local/bin/prometheus
chown prometheus:prometheus /usr/local/bin/promtool

# Copy console files
cp -r /home/onecloud/prometheus-files/consoles /etc/prometheus
cp -r /home/onecloud/prometheus-files/console_libraries /etc/prometheus
chown -R prometheus:prometheus /etc/prometheus/consoles
chown -R prometheus:prometheus /etc/prometheus/console_libraries

# Create Prometheus configuration file
cat <<EOL > /etc/prometheus/prometheus.yml
global:
  scrape_interval: 10s

scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:9090']
EOL

# Set ownership for the configuration file
chown prometheus:prometheus /etc/prometheus/prometheus.yml

# Create systemd service file for Prometheus
cat <<EOL > /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd daemon
systemctl daemon-reload


