# 1. Створення групи ANA з ідентифікатором 1 для мережевого порту 1
mkdir -p /sys/kernel/config/nvmet/ports/1/ana_groups/1

# 2. Призначення стану Optimized для цієї групи на порту 1
echo "optimized" > /sys/kernel/config/nvmet/ports/1/ana_groups/1/state

# 3. Створення тієї самої групи ANA 1 на резервному мережевому порту 2 зі станом Non-Optimized
mkdir -p /sys/kernel/config/nvmet/ports/2/ana_groups/1
echo "non-optimized" > /sys/kernel/config/nvmet/ports/2/ana_groups/1/state

# 4. Прив'язка простору назв 1 цільової підсистеми до створеної групи ANA 1
echo 1 > /sys/kernel/config/nvmet/subsystems/nvme-subsys-test/namespaces/1/ana_grpid
