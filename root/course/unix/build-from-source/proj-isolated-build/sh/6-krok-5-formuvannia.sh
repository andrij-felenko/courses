# Створення цільових каталогів
mkdir -p /tmp/build-workspace/stage/opt/netbridge/{bin,etc}
mkdir -p /tmp/build-workspace/stage/etc/systemd/system

# Розміщення виконуваного файлу
cp netbridge /tmp/build-workspace/stage/opt/netbridge/bin/
chmod 755 /tmp/build-workspace/stage/opt/netbridge/bin/netbridge

# Створення файлу конфігурації
cat << 'EOF' > /tmp/build-workspace/stage/opt/netbridge/etc/netbridge.conf
# Конфігурація сервісу netbridge
PORT=8080
WORKERS=4
LOG_LEVEL=info
EOF

# Створення systemd сервіс-юніта
cat << 'EOF' > /tmp/build-workspace/stage/etc/systemd/system/netbridge.service
[Unit]
Description=NetBridge Custom Network Gateway
After=network.target

[Service]
Type=simple
ExecStart=/opt/netbridge/bin/netbridge
Restart=on-failure
User=nobody
Group=nogroup
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF
