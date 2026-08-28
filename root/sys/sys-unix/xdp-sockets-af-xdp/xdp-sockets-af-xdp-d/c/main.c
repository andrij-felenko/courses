SEC("xdp")
int xdp_redirect_to_xsk(struct xdp_md *ctx) {
    int rx_queue_index = ctx->rx_queue_index;

    // Перевіряємо, чи підключено сокет AF_XDP до цієї черги
    if (bpf_map_lookup_elem(&xsks_map, &rx_queue_index)) {
        return bpf_redirect_map(&xsks_map, rx_queue_index, 0);
    }

    return XDP_PASS; // Передаємо решту трафіку звичайному ядру
}
