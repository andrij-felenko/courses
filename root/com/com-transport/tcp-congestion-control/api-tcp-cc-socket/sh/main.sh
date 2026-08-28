# Переглянути алгоритм за замовчуванням
sysctl net.ipv4.tcp_congestion_control

# Переглянути завантажені алгоритми у ядрі
cat /proc/sys/net/ipv4/tcp_available_congestion_control

# Переглянути дозволені для непривілейованих користувачів алгоритми
cat /proc/sys/net/ipv4/tcp_allowed_congestion_control

# Динамічно переключити глобальний алгоритм на BBR (потрібні права root / sudo)
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr

# Додати BBR до списку дозволених для всіх користувачів
sudo sysctl -w net.ipv4.tcp_allowed_congestion_control="cubic reno bbr"
