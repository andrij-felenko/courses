# 1. Перевірка ідентифікатора зони сокета
cat /sys/class/powercap/intel-rapl/intel-rapl:0/name
# Очікуване значення: package-0

# 2. Встановлення ліміту довготривалої потужності PL1
echo 65000000 | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw

# 3. Встановлення часового вікна для ліміту PL1
echo 15000000 | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_time_window_us

# 4. Активація контролю зони
echo 1 | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:0/enabled

# 5. Перевірка фактично встановлених параметрів
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_time_window_us
