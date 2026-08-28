#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include <linux/udp.h>
#include <linux/in.h>

/* Допоміжна функція для заміни місцями MAC-адрес у Ethernet-заголовку */
static __always_inline void swap_mac_addresses(struct ethhdr *eth) {
    unsigned char tmp[ETH_ALEN];
    __builtin_memcpy(tmp, eth->h_dest, ETH_ALEN);
    __builtin_memcpy(eth->h_dest, eth->h_source, ETH_ALEN);
    __builtin_memcpy(eth->h_source, tmp, ETH_ALEN);
}

/* Допоміжна функція для заміни місцями IP-адрес у IPv4-заголовку */
static __always_inline void swap_ip_addresses(struct iphdr *iph) {
    __be32 tmp = iph->saddr;
    iph->saddr = iph->daddr;
    iph->daddr = tmp;
}

SEC("xdp")
int xdp_router_filter(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    /* 1. Bounds check для Ethernet-заголовка */
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end) {
        return XDP_PASS;
    }

    /* Перевіряємо, чи це IPv4 пакет */
    if (eth->h_proto != __builtin_htons(ETH_P_IP)) {
        return XDP_PASS;
    }

    /* 2. Bounds check для IP-заголовка */
    struct iphdr *iph = (void *)(eth + 1);
    if ((void *)(iph + 1) > data_end) {
        return XDP_PASS;
    }

    /* Перевірка випадків UDP трафіку */
    if (iph->protocol == IPPROTO_UDP) {
        struct udphdr *udph = (void *)iph + (iph->ihl * 4);
        if ((void *)(udph + 1) > data_end) {
            return XDP_PASS;
        }

        /* Якщо порт призначення 9999 — миттєво відкидаємо пакет (XDP_DROP) */
        if (udph->dest == __builtin_htons(9999)) {
            return XDP_DROP;
        }
    }

    /* Перевірка випадків ICMP Echo Request */
    if (iph->protocol == IPPROTO_ICMP) {
        struct icmphdr *icmph = (void *)iph + (iph->ihl * 4);
        if ((void *)(icmph + 1) > data_end) {
            return XDP_PASS;
        }

        /* Якщо це ICMP Echo Request (тип 8) */
        if (icmph->type == ICMP_ECHO) {
            /* Змінюємо тип на ICMP Echo Reply (тип 0) */
            icmph->type = ICMP_ECHOREPLY;
            
            /* Інкрементально оновлюємо контрольну суму ICMP (різниця типів 8 -> 0 дорівнює +0x0008) */
            icmph->checksum += 0x0008;

            /* Міняємо місцями джерело та призначення для MAC та IP */
            swap_mac_addresses(eth);
            swap_ip_addresses(iph);

            /* Відправляємо пакет назад через той самий мережевий адаптер (XDP_TX) */
            return XDP_TX;
        }
    }

    /* Усі інші пакети пропускаємо у стандартний стек ядра (XDP_PASS) */
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
