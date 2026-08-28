# 1. Читання поточного стану forwarding IPv4
./mini_sysctl_c net.ipv4.ip_forward
# Вивід: net.ipv4.ip_forward = 0

# 2. Спроба запису нового значення без привілеїв root
./mini_sysctl_c net.ipv4.ip_forward 1
# Вивід: Помилка доступу до /proc/sys/net/ipv4/ip_forward: потрібні привілеї root (CAP_SYS_ADMIN або CAP_NET_ADMIN)

# 3. Запис із привілеями суперкористувача root
sudo ./mini_sysctl_cpp net.ipv4.ip_forward 1
# Вивід: net.ipv4.ip_forward = 1

# 4. Перевірка результату запису
./mini_sysctl_c net.ipv4.ip_forward
# Вивід: net.ipv4.ip_forward = 1

# 5. Спроба запису неприпустимого значення (перевірка minmax у ядрі)
sudo ./mini_sysctl_c vm.swappiness 300
# Вивід: Помилка запису у /proc/sys/vm/swappiness: недопустиме значення '300' (поза діапазоном або хибний тип)
