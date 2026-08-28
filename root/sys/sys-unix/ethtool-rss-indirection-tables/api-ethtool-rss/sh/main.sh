# 1. Перегляд поточної конфігурації апаратних черг (Channels)
ethtool -l eth0

# 2. Зміна кількості комбінованих черг прийому/передачі (Combined Rx/Tx)
sudo ethtool -L eth0 combined 8

# 3. Перегляд таблиці RETA, секретного ключа RSS та активної хеш-функції
ethtool -x eth0

# 4. Встановлення рівномірного розподілу комірок RETA між 8 чергами
sudo ethtool -X eth0 equal 8

# 5. Встановлення зваженого розподілу ваг RETA (Черга 0 вимкнена, Черга 1: 50%, Черги 2 і 3: по 25%)
sudo ethtool -X eth0 weight 0 2 1 1

# 6. Перегляд полів хешування (n-tuple) для протоколу TCP v4
ethtool -n eth0 rx-flow-hash tcp4

# 7. Увімкнення повного 4-tuple хешування для UDP v4 (Src IP, Dst IP, Src Port, Dst Port)
sudo ethtool -N eth0 rx-flow-hash udp4 sdfn
