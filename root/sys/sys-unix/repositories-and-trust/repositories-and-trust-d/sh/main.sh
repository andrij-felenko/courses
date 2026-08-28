# 1. Створення ізольованого каталогу для ключів із правильними правами доступу
sudo install -m 0755 -d /etc/apt/keyrings

# 2. Завантаження ключа та збереження його у форматі keyring або ASCII-armored
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 3. Створення конфігурації репозиторію з чіткою прив'язкою signed-by
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64 arm64
Signed-By: /etc/apt/keyrings/docker.gpg
EOF
