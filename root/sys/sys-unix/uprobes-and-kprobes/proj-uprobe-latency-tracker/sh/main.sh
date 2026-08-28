# Компіляція target_app
gcc -O2 target_app.c -o target_app

# Компіляція eBPF програми та генерація скелета libbpf
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c uprobe_tracer.bpf.c -o uprobe_tracer.bpf.o
bpftool gen skeleton uprobe_tracer.bpf.o > uprobe_tracer.skel.h

# Компіляція завантажувача (C та C++)
gcc -O2 tracer.c -lbpf -o tracer_c
g++ -O2 -std=c++17 tracer.cpp -lbpf -o tracer_cpp
