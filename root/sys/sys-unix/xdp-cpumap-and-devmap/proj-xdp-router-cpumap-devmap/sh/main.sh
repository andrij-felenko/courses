# 1. Компіляція eBPF програмою під цільову архітектуру bpf
clang -O2 -g -target bpf -c xdp_router_kern.c -o xdp_router_kern.o

# 2. Компіляція C завантажувача
gcc -O2 loader.c -o loader_c -lbpf

# 3. Компіляція C++ завантажувача
g++ -O2 -std=c++20 loader.cpp -o loader_cpp -lbpf

# 4. Створення віртуальної мережевої тестової пари veth
sudo ip link add veth0 type veth peer name veth1
sudo ip link set dev veth0 up
sudo ip link set dev veth1 up

# 5. Запуск маршрутизатора між veth0 та veth1
sudo ./loader_cpp veth0 veth1
