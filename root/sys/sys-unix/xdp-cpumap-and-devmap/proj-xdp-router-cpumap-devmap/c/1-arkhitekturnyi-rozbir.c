#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

/* BPF-карта CPUMAP для розпаралелювання обробки між ядрами */
struct {
    __uint(type, BPF_MAP_TYPE_CPUMAP);
    __uint(max_entries, 64);
    __type(key, __u32);   /* cpu_id */
    __type(value, struct bpf_cpumap_val);
} cpu_map SEC(".maps");

/* BPF-карта DEVMAP для прямого виводу кадра в TX-інтерфейс */
struct {
    __uint(type, BPF_MAP_TYPE_DEVMAP);
    __uint(max_entries, 256);
    __type(key, __u32);   /* ifindex */
    __type(value, struct bpf_devmap_val);
} tx_dev_map SEC(".maps");

/* Допоміжна функція L2 rewrite (заміна MAC-адрес) */
static __always_inline int rewrite_mac(struct xdp_md *ctx, unsigned char *src_mac, unsigned char *dst_mac)
{
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;
    struct ethhdr *eth = data;

    if ((void *)(eth + 1) > data_end)
        return -1;

    __builtin_memcpy(eth->h_dest, dst_mac, ETH_ALEN);
    __builtin_memcpy(eth->h_source, src_mac, ETH_ALEN);
    return 0;
}

SEC("xdp")
int xdp_router_entry(struct xdp_md *ctx)
{
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;
    struct ethhdr *eth = data;

    /* Перевірка меж пам'яті для BPF Verifier */
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;

    /* Працюємо лише з IP-пакетами */
    if (eth->h_proto != bpf_htons(ETH_P_IP))
        return XDP_PASS;

    struct iphdr *iph = (void *)(eth + 1);
    if ((void *)(iph + 1) > data_end)
        return XDP_PASS;

    /* Простий приклад балансування: парні IP на CPU 1, непарні на DEVMAP port 2 */
    __u32 src_ip = bpf_ntohl(iph->saddr);
    
    if (src_ip % 2 == 0) {
        /* Скеровуємо на CPU 1 через CPUMAP */
        __u32 target_cpu = 1;
        return bpf_redirect_map(&cpu_map, target_cpu, XDP_PASS);
    } else {
        /* L2 rewrite та пряме перенаправлення на eth1 (ifindex = 2) */
        unsigned char next_hop_mac[6] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55};
        unsigned char src_port_mac[6] = {0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE};

        if (rewrite_mac(ctx, src_port_mac, next_hop_mac) < 0)
            return XDP_DROP;

        __u32 target_ifindex = 2;
        return bpf_redirect_map(&tx_dev_map, target_ifindex, XDP_ABORTED);
    }
}

char _license[] SEC("license") = "GPL";
