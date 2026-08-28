// Виклик усередині програми eBPF XDP:
extern int bpf_xdp_metadata_rx_timestamp(const struct xdp_md *ctx, __u64 *timestamp) __ksym;

SEC("xdp")
int filter_ptp_fast(struct xdp_md *ctx) {
    __u64 hw_timestamp_ns = 0;
    if (bpf_xdp_metadata_rx_timestamp(ctx, &hw_timestamp_ns) == 0) {
        // Доступ до сирої наносекундної мітки з апаратного дескриптора RX
        // Обробка або передача в AF_XDP сокет через кільце UMEM
    }
    return XDP_PASS;
}
