# 1. Компіляція eBPF програми у байткод BPF
clang -O2 -g -target bpf -c xdp_redirect_kern.c -o xdp_redirect_kern.o

# 2. Завантаження eBPF програми на мережевий інтерфейс eth0
bpftool prog load xdp_redirect_kern.o /sys/fs/bpf/xdp_redirect_app type xdp
bpftool net attach xdp id $(bpftool prog show pinned /sys/fs/bpf/xdp_redirect_app | awk '{print $1}' | tr -d ':') dev eth0

# 3. Компіляція додатка простору користувача (C)
gcc -O3 xsk_app.c -o xsk_app -lxdp -lbpf

# 4. Компіляція додатка простору користувача (C++)
g++ -O3 -std=c++20 xsk_app.cpp -o xsk_app_cpp -lxdp -lbpf
