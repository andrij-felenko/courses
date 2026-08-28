# 1. Генерація системного заголовка vmlinux.h із поточного завантаженого ядра
$ bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

# 2. Компіляція ядерного коду у цільовий байткод BPF
$ clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -I. -c packet_probe.bpf.c -o packet_probe.bpf.o

# 3. Автоматична генерація C-скелета через bpftool
$ bpftool gen skeleton packet_probe.bpf.o > packet_probe.skel.h

# 4. Збирання бінарного файлу простору користувача мовою C
$ gcc -O2 -g main.c -lbpf -lelf -lz -o packet_tracer_c

# 5. Збирання бінарного файлу простору користувача мовою C++
$ g++ -O2 -std=c++20 main.cpp -lbpf -lelf -lz -o packet_tracer_cpp
