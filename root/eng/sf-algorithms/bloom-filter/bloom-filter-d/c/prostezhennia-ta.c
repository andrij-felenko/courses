#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_BLOOM_FILTER);
    __uint(key_size, 0);
    __uint(value_size, sizeof(uint32_t));
    __uint(max_entries, 1000000);
    __uint(map_extra, 5); /* k = 5 хеш-функцій */
} bloom_map SEC(".maps");

SEC("xdp")
int filter_packets(struct xdp_md *ctx) {
    uint32_t src_ip = 0x01020304;
    /* Перевірка IP у фільтрі Блума eBPF */
    long err = bpf_map_peek_elem(&bloom_map, &src_ip);
    if (err == -ENOENT) {
        /* Елемента немає в базі - пропускаємо пакет */
        return XDP_PASS;
    }
    return XDP_DROP;
}
