// xdp_redirect_kern.c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

struct {
    __uint(type, BPF_MAP_TYPE_XSKMAP);
    __uint(max_entries, 64);
    __type(key, int);
    __type(value, int);
} xsks_map SEC(".maps");

SEC("xdp")
int xdp_redirect_xsk(struct xdp_md *ctx) {
    int rx_queue_index = ctx->rx_queue_index;

    // Перевіряємо, чи є підключений сокет AF_XDP для цієї черги
    if (bpf_map_lookup_elem(&xsks_map, &rx_queue_index)) {
        return bpf_redirect_map(&xsks_map, rx_queue_index, 0);
    }

    // Якщо сокет відсутній, передаємо пакет стандартному стеку ядра
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
