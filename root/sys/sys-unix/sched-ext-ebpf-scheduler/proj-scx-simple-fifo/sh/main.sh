# 1. Генерація vmlinux.h та BPF-скелета
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
clang -g -O2 -target bpf -c my_fifo.bpf.c -o my_fifo.bpf.o
bpftool gen skeleton my_fifo.bpf.o > my_fifo.skel.h

# 2. Збірка завантажувача C та C++
gcc -O2 my_fifo.c -lbpf -o loader_c
g++ -O2 -std=c++20 my_fifo.cpp -lbpf -o loader_cpp

# 3. Запуск під привілеями root
sudo ./loader_c
