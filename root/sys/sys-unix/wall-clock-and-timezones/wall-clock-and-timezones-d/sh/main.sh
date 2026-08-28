# Переглянути список усіх доступних часових поясів з бази IANA
timedatectl list-timezones | grep -i kyiv

# Встановити часовий пояс (systemd-timedated атомарно оновлює /etc/localtime)
timedatectl set-timezone Europe/Kyiv

# Встановити системний час вручну (лише при вимкненому NTP)
timedatectl set-time "2026-08-25 20:00:00"

# Переконатися, що RTC працює в режимі UTC (значення 0 = UTC, значення 1 = Local Time)
timedatectl set-local-rtc 0

# Увімкнути або вимкнути службу автоматичної синхронізації NTP
timedatectl set-ntp true
