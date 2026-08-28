# 1. Увімкнення апаратного збереження хешу в RTC
sudo sh -c "echo 1 > /sys/power/pm_trace"

# 2. Спроба переходу в сон
sudo sh -c "echo mem > /sys/power/state"

# 3. Якщо система зависла — виконуємо апаратний скид (кнопкою живлення / Reset),
# після завантаження читаємо винуватця збігу збереженого хешу:
sudo dmesg | grep "Magic number"
cat /sys/power/pm_trace_dev_match
