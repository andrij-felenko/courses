# 1. Дамп системних типів ядра у форматі BTF C-header
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

# 2. Компіляція BPF-програми у цільову архітектуру BPF
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c bpf_lsm_exec.bpf.c -o bpf_lsm_exec.bpf.o

# 3. Компіляція завантажувача мовою C++ з підтримкою C++20
g++ -O2 -std=c++20 lsm_loader.cpp -lbpf -o lsm_loader

# 4. Перевірка наявності bpf у переліку увімкнених LSM-модулів
cat /sys/kernel/security/lsm

# 5. Запуск монітора з привілеями суперкористувача (CAP_SYS_ADMIN / CAP_BPF)
sudo ./lsm_loader
