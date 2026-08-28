# 1. Спроба перейменувати активний інтерфейс завершується помилкою ядра:
$ sudo ip link set dev enp3s0 up
$ sudo ./rename_net_c enp3s0 mylan0
Ядро відхилило операцію перейменування: Device or resource busy (-16)

# 2. Правильна послідовність: зупинка інтерфейсу -> перейменування -> підняття
$ sudo ip link set dev enp3s0 down
$ sudo ./rename_net_c enp3s0 mylan0
Інтерфейс успішно перейменовано: enp3s0 -> mylan0 (ifindex: 2)

$ sudo ip link set dev mylan0 up
