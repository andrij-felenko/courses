# 1. Створення каталогу декларативних залежностей таргета
sudo mkdir -p /etc/systemd/system/kiosk.target.wants

# 2. Створення юнітів служб додатків кіоску
sudo tee /etc/systemd/system/kiosk-browser.service > /dev/null << 'EOF'
[Unit]
Description=Kiosk Browser Application
After=graphical.target

[Service]
Type=simple
ExecStart=/usr/bin/chromium --kiosk --incognito https://localhost/kiosk
Restart=always
RestartSec=3s
User=kioskuser

[Install]
WantedBy=kiosk.target
EOF

sudo tee /etc/systemd/system/kiosk-watchdog.service > /dev/null << 'EOF'
[Unit]
Description=Kiosk Hardware Watchdog Daemon

[Service]
Type=simple
ExecStart=/usr/local/bin/kiosk-watchdog-daemon
Restart=always
User=root

[Install]
WantedBy=kiosk.target
EOF

# 3. Прив'язка служб до таргета через символьні посилання
sudo ln -sf /etc/systemd/system/kiosk-browser.service \
  /etc/systemd/system/kiosk.target.wants/kiosk-browser.service

sudo ln -sf /etc/systemd/system/kiosk-watchdog.service \
  /etc/systemd/system/kiosk.target.wants/kiosk-watchdog.service

# 4. Перезавантаження конфігурації PID 1 для зчитування нових таргетів
sudo systemctl daemon-reload
