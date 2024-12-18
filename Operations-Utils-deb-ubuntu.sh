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
curl https://baltocdn.com/helm/signing.asc -o signing.asc
gpg --dearmor signing.asc
sudo mv signing.asc.gpg /usr/share/keyrings/helm.gpg
rm signing.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" > helm-stable-debian.list
sudo mv helm-stable-debian.list /etc/apt/sources.list.d/helm-stable-debian.list


sudo apt-get update
sleep 5s
sudo apt-get install apt-transport-https --yes
sudo apt-get install helm

#terraform install
wget -O hashicorp.gpg https://apt.releases.hashicorp.com/gpg
sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg hashicorp.gpg
rm hashicorp.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > hashicorp.list
sudo mv hashicorp.list /etc/apt/sources.list.d/hashicorp.list

sudo apt update
sleep 5s
sudo apt install terraform

#install ansible
sudo apt install software-properties-common -y
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible -y


#This part is only for Debian OS to fix the locale issue!

#!/bin/bash

# Get the operating system information
OS_NAME=$(lsb_release -d | awk -F'\t' '{print $2}')

# Check if the OS is Debian 12
if [[ "$OS_NAME" == "Debian GNU/Linux 12 (bookworm)" ]]; then
  echo "Detected OS: $OS_NAME. Proceeding with locale configuration..."

  # Add missing locale to /etc/locale.gen
  echo "Ensuring required locales are available..."
  REQUIRED_LOCALE="ar_LY.UTF-8 UTF-8"
  LOCALE_GEN_FILE="/etc/locale.gen"

  if ! grep -q "^$REQUIRED_LOCALE" "$LOCALE_GEN_FILE"; then
    echo "$REQUIRED_LOCALE" | sudo tee -a "$LOCALE_GEN_FILE"
  else
    echo "Locale $REQUIRED_LOCALE already exists in $LOCALE_GEN_FILE."
  fi

  # Generate locales
  echo "Generating locales..."
  sudo locale-gen

  # Set system-wide locale
  echo "Setting system-wide locale..."
  DEFAULT_LOCALE_FILE="/etc/default/locale"
  sudo bash -c "cat > $DEFAULT_LOCALE_FILE" <<EOL
LANG=C.UTF-8
LC_ALL=ar_LY.UTF-8
EOL

  # Export locale environment variables
  echo "Exporting locale environment variables..."
  PROFILE_FILE="/etc/profile"
  if ! grep -q "export LC_ALL=ar_LY.UTF-8" "$PROFILE_FILE"; then
    sudo bash -c "cat >> $PROFILE_FILE" <<EOL

# Locale settings
export LANG=C.UTF-8
export LC_ALL=ar_LY.UTF-8
EOL
  fi

  # Apply changes
  echo "Applying locale changes..."
  source /etc/profile

  # Verify locales
  echo "Verifying locale settings..."
  locale

  echo "Locale setup complete!"
fi


