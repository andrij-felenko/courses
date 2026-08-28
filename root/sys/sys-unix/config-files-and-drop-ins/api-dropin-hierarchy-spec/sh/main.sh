# Повний звіт про всі конфігураційні зміни системи
systemd-delta

# Фільтрація лише замаскованих та перевизначених файлів
systemd-delta --type=masked,overridden

# Показ конкретного diff для змінених файлів
systemd-delta --diff=yes

# Перевірка лише конкретної підсистеми
systemd-delta sysctl.d/
systemd-delta udev/rules.d/
