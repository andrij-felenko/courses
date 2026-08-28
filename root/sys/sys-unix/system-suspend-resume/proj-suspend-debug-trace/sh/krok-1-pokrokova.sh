# 1. Перевірка підсистеми заморожування процесів (Freezer)
sudo sh -c "echo freezer > /sys/power/pm_test"
sudo sh -c "echo mem > /sys/power/state"

# 2. Перевірка зворотних викликів драйверів пристроїв (DPM)
sudo sh -c "echo devices > /sys/power/pm_test"
sudo sh -c "echo mem > /sys/power/state"

# 3. Перевірка платформних викликів ACPI / Device Tree
sudo sh -c "echo platform > /sys/power/pm_test"
sudo sh -c "echo mem > /sys/power/state"

# 4. Перевірка відключення вторинних ядер процесора (CPU Hotplug)
sudo sh -c "echo processors > /sys/power/pm_test"
sudo sh -c "echo mem > /sys/power/state"

# 5. Перевірка зупинки системних переривань (syscore)
sudo sh -c "echo core > /sys/power/pm_test"
sudo sh -c "echo mem > /sys/power/state"

# Повернення до нормального режиму після завершення тестів
sudo sh -c "echo none > /sys/power/pm_test"
