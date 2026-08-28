# Перевірка поточного статусу зондування MTU в ядрі
sysctl net.ipv4.tcp_mtu_probing

# Активація автоматичного зондування при виявленні "чорних дір" (значення 1)
sudo sysctl -w net.ipv4.tcp_mtu_probing=1

# Примусове постійне зондування для всіх вихідних TCP-з'єднань (значення 2)
sudo sysctl -w net.ipv4.tcp_mtu_probing=2

# Налаштування базового початкового MSS для виходу з блокування
sudo sysctl -w net.ipv4.tcp_base_mss=1024
