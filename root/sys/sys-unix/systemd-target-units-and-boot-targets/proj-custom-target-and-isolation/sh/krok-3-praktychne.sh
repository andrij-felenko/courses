# 1. Запуск ізоляції та перехід у створений kiosk.target
sudo ./isolate-cpp kiosk.target

# 2. Перевірка списку активних таргетів у системі
systemctl list-units --type=target --state=active

# 3. Перевірка стану створених служб кіоску
systemctl status kiosk-browser.service kiosk-watchdog.service

# 4. Перевірка системного журналу транзакцій PID 1
sudo journalctl -u kiosk.target -n 20

# 5. Повернення системи у стандартний багатокористувацький режим
sudo ./isolate-c multi-user.target
