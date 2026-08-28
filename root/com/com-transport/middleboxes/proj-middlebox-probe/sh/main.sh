# 1. Компіляція бінарного файлу C++23
g++ -O2 -std=c++23 -Wall -Wextra proj-middlebox-probe.cpp -o probe_scanner

# 2. Надання бінарнику дозволу на сирі сокети без root-прав (опціонально)
sudo setcap cap_net_raw+ep probe_scanner

# 3. Блокування автоматичних RST локального ядра Linux
sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST --sport 54321 -j DROP

# 4. Запуск зондування цільового сервера
./probe_scanner 192.168.1.50 93.184.216.34 54321 80
