# Створення конфігураційного файлу:
echo -e "EXEC=/usr/bin/python3\nPORT=9090" | sudo tee /etc/custom-app.conf

# Виконання перезавантаження конфігураційного графа PID 1:
sudo systemctl daemon-reload

# Перевірка згенерованого файлу в оперативній пам'яті:
ls -la /run/systemd/generator/custom-app.service
cat /run/systemd/generator/custom-app.service

# Перевірка статусу юніта через systemctl:
systemctl status custom-app.service
