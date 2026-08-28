// Структура BPF-мапи для накопичення метрик у ядрі Linux
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __type(key, __u32);
    __type(value, __u64);
    __uint(max_entries, 4); // [0]=TN, [1]=FP, [2]=FN, [3]=TP
} metrics_map SEC(".maps");

SEC("xdp")
int xdp_metrics_monitor(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data     = (void *)(long)ctx->data;

    // Швидкий розбір Ethernet / IP заголовків
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;

    if (eth->h_proto != __constant_htons(ETH_P_IP))
        return XDP_PASS;

    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end)
        return XDP_PASS;

    // Визначення істинної мітки (y) та прогнозу моделі (y_hat)
    __u8 actual = (ip->protocol == IPPROTO_UDP) ? 1 : 0; // Наприклад, атака UDP Flood
    __u8 pred   = (ip->tos & 0x01) ? 1 : 0;              // Ознака, виставлена класифікатором

    __u32 index = ((__u32)actual << 1) | (__u32)pred;
    __u64 *counter = bpf_map_lookup_elem(&metrics_map, &index);
    if (counter) {
        (*counter)++;
    }

    return (pred == 1) ? XDP_DROP : XDP_PASS;
}
