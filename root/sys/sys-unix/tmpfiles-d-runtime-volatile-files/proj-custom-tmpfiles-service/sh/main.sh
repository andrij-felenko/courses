# 1. Перевірка синтаксису конфігурації у тестовому режимі без внесення змін (dry-run)
systemd-tmpfiles --create --dry-run /etc/tmpfiles.d/appdaemon.conf

# 2. Фактичне застосування конфігураційних правил до файлової системи
systemd-tmpfiles --create /etc/tmpfiles.d/appdaemon.conf

# 3. Перевірка атрибутів створеного каталогу та файлу стану
ls -ld /run/appdaemon
ls -l /run/appdaemon/status

# 4. Моделювання виконання процедури очищення тимчасових файлів
systemd-tmpfiles --clean /etc/tmpfiles.d/appdaemon.conf
