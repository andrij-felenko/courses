// eBPF C-код для оновлення лічильника пакетів у мапі
SEC("xdp")
int xdp_packet_counter(struct xdp_md *ctx)
{
    u32 key = 0;
    u64 *count = bpf_map_lookup_elem(&pkt_count_map, &key);
    if (count) {
        // Компілятор породжує BPF-інструкцію BPF_ADD із модифікатором BPF_ATOMIC
        __sync_fetch_and_add(count, 1);
    }
    return XDP_PASS;
}
