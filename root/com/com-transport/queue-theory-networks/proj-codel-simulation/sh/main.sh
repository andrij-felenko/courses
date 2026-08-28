# Створення пари віртуальних мережевих інтерфейсів
sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth0 up
sudo ip link set veth1 up

# Встановлення швидкості лінії 10 Мбіт/с та базової затримки 20 мс
sudo tc qdisc add dev veth0 root handle 1: netem delay 20ms rate 10Mbit

# Підключення алгоритму FQ-CoDel як внутрішньої дисципліни черги
sudo tc qdisc add dev veth0 parent 1:1 handle 10: fq_codel target 5ms interval 100ms

# Запуск тесту RRUL (Realtime Response Under Load)
flent rrul -p all_scaled -l 60 -H 192.168.1.2 -o test_codel.png
