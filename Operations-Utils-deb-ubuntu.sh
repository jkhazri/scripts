#!/bin/bash

# Install curl if not installed
sudo apt-get install -y curl

  # Get the OS ID and codename
  OS_ID=$(grep -oP '(?<=^ID=).*' /etc/os-release | tr -d '"')
  OS_CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")

  # Update and install dependencies
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl

  # Set up Docker GPG key and repository
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc

  # Add the Docker repository based on the OS
  if [ "$OS_ID" = "debian" ]; then
    sudo echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $OS_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  elif [ "$OS_ID" = "ubuntu" ]; then
    sudo echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $OS_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  fi

  # Update apt package list and install Docker packages
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  # Restart Docker service
  sudo systemctl restart docker

# Download the latest version of Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Set executable permissions
sudo chmod +x /usr/local/bin/docker-compose

#install K9S
wget -P /tmp https://github.com/derailed/k9s/releases/download/v0.32.6/k9s_linux_amd64.deb

sudo apt install /tmp/k9s_linux_amd64.deb
sudo rm -f /tmp/k9s_linux_amd64.deb


#install kubectl

curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# kubeseal install
curl -OL "https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.27.3/kubeseal-0.27.3-linux-amd64.tar.gz"
tar -xvzf kubeseal-0.27.3-linux-amd64.tar.gz kubeseal
sudo install -m 755 kubeseal /usr/local/bin/kubeseal


#install terragrunt

wget -P /tmp https://github.com/gruntwork-io/terragrunt/releases/download/v0.69.9/terragrunt_linux_amd64

mv /tmp/terragrunt_linux_amd64 /tmp/terragrunt
chmod u+x /tmp/terragrunt
mv /tmp/terragrunt /usr/local/bin/terragrunt

#Installing jq and yq
sudo apt-get install -y jq 
sudo wget https://github.com/mikefarah/yq/releases/download/v4.44.6/yq_linux_amd64
sudo mv yq_linux_amd64 /usr/bin/yq
sudo chmod +x /usr/bin/yq

# helm install
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

#terraform install
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

#install ansible
sudo apt install software-properties-common -y
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible -y
