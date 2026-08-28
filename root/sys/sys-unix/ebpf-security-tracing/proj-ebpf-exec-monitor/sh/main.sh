# Крок 1: Дамп системних типів BTF з поточного ядра Linux у vmlinux.h
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

# Крок 2: Компіляція BPF-коду ядра у BPF-байткод (об'єктний файл)
# Прапор -g є обов'язковим для збереження метаданих DWARF/BTF
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c exec_monitor.bpf.c -o exec_monitor.bpf.o

# Крок 3: Генерація C-скелета (header-only файлу) за допомогою bpftool
bpftool gen skeleton exec_monitor.bpf.o > exec_monitor.skel.h

# Крок 4а: Збірка демона на мові C
gcc -O2 -g exec_monitor.c -lbpf -lelf -lz -o exec_monitor

# Крок 4б: Збірка демона на мові C++20
g++ -O2 -g -std=c++20 exec_monitor.cpp -lbpf -lelf -lz -o exec_monitor_cpp

# Крок 5: Запуск із системними привілеями CAP_BPF / root
sudo ./exec_monitor
