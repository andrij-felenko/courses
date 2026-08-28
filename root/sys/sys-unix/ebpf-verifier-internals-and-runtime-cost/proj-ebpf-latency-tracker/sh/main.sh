# 1. Компіляція байт-коду ядра eBPF
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -I/usr/include -c openat_tracker.bpf.c -o openat_tracker.bpf.o

# 2. Опціональна генерація C-скелета (bpftool gen skeleton)
bpftool gen skeleton openat_tracker.bpf.o > openat_tracker.skel.h

# 3. Компіляція програми простору користувача на C
gcc -O2 -g -Wall openat_tracker.c -lbpf -lelf -lz -o openat_tracker

# 4. Запуск з привілеями CAP_BPF та CAP_PERFMON (або root)
sudo ./openat_tracker
