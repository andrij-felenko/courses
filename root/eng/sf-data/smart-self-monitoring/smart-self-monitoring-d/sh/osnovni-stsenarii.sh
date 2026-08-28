# Загальна інформація про пристрій (модель, серійний номер, версія прошивки)
smartctl -i /dev/sda

# Експрес-оцінка здоров'я (SMART Overall Health Assessment)
smartctl -H /dev/sda

# Вивід повної таблиці атрибутів (для SATA)
smartctl -A /dev/sda

# Детальний звіт про здоров'я накопичувача NVMe
smartctl -a /dev/nvme0

# Опитування диска SATA, підключеного через апаратний RAID-контролер MegaRAID
smartctl -d megaraid,0 -a /dev/sda

# Опитування диска в USB-кишені з мостом SAT
smartctl -d sat -a /dev/sdb
