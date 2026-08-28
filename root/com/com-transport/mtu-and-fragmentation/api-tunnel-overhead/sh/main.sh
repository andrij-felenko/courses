# Автоматичний розрахунок і затискання MSS відповідно до PMTU вихідного інтерфейсу
sudo iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN \
    -j TCPMSS --clamp-mss-to-pmtu

# Примусове встановлення фіксованого значення MSS для конкретного VPN-інтерфейсу
sudo iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN \
    -o wg0 -j TCPMSS --set-mss 1380

# Аналогічні правила для транзитного трафіку IPv6
sudo ip6tables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN \
    -j TCPMSS --clamp-mss-to-pmtu
