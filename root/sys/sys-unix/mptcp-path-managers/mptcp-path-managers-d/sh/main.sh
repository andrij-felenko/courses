# 1. Переконатися, що увімкнено In-Kernel Path Manager
sysctl -w net.mptcp.pm_type=0

# 2. Встановити глобальні ліміти: до 3 підпотоків та 2 оголошень
ip mptcp limits set subflows 3 add_addr_accepted 2

# 3. Додати eth0 як локальну кінцеву точку для оголошення адреси
ip mptcp endpoint add 192.168.1.100 dev eth0 id 1 signal

# 4. Додати wlan0 як активний резервний підпотік
ip mptcp endpoint add 10.0.0.15 dev wlan0 id 2 subflow backup
