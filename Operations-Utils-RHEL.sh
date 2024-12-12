#!/bin/bash

# install docker
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo systemctl restart docker  

# Download the latest version of Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# install k9s_linux
sudo rpm -ivh https://github.com/derailed/k9s/releases/download/v0.32.7/k9s_linux_amd64.rpm


#install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/bin/kubectl


# kubeseal install
curl -OL "https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.27.3/kubeseal-0.27.3-linux-amd64.tar.gz"
tar -xvzf kubeseal-0.27.3-linux-amd64.tar.gz kubeseal
sudo install -m 755 kubeseal /usr/bin/kubeseal

# helm install
curl -LO https://get.helm.sh/helm-v3.13.0-linux-amd64.tar.gz
tar -zxvf helm-v3.13.0-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/bin/helm

#terraform install

sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo yum -y install terraform

#install terragrunt

wget -P /tmp https://github.com/gruntwork-io/terragrunt/releases/download/v0.69.9/terragrunt_linux_amd64

mv /tmp/terragrunt_linux_amd64 /tmp/terragrunt
chmod u+x /tmp/terragrunt
mv /tmp/terragrunt /usr/bin/terragrunt

#Installing jq and yq
dnf install -y jq
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq
chmod +x /usr/bin/yq 

# ansible install
sudo yum install epel-release -y
sudo yum install ansible -y
# Check if the OS is AlmaLinux and version 8.9
OS_NAME=$(grep ^NAME= /etc/os-release | cut -d'=' -f2 | tr -d '"')
OS_VERSION=$(grep ^VERSION= /etc/os-release | cut -d'=' -f2 | tr -d '"')

if [[ "$OS_NAME" == "AlmaLinux" && "$OS_VERSION" == "8.9 (Midnight Oncilla)" ]]; then
    echo "LANG=en_US.UTF-8" | sudo tee /etc/locale.conf
    source /etc/locale.conf
    export LANG=en_US.UTF-8
    export LC_ALL=en_US.UTF-8
    echo "export LANG=en_US.UTF-8" >> /root/.bashrc
    echo "export LC_ALL=en_US.UTF-8" >> /root/.bashrc
    source /root/.bashrc

    

