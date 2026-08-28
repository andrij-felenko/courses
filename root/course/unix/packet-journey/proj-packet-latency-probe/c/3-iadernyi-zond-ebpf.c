#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";

/* Структура події, яка передається в простір користувача */
struct event_t {
    __u64 skb_addr;
    __u64 latency_softirq_us;
    __u64 latency_netfilter_us;
    __u64 latency_total_us;
    __u32 src_ip;
    __u32 dst_ip;
    __u16 src_port;
    __u16 dst_port;
    __u16 protocol;
    __u32 drop_reason;
    char ifname[16];
};

/* Геш-таблиця збереження часових міток для активних sk_buff */
struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, 65536);
    __type(key, __u64);   /* skb_addr */
    __type(value, __u64); /* t_ingress_ns */
} skb_timestamps SEC(".maps");

/* Спільний кільцевий буфер подій */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

/* 1. Точка входу: пакет отримано з драйвера */
SEC("tracepoint/net/netif_receive_skb")
int trace_netif_receive_skb(struct trace_event_raw_netif_receive_skb *ctx)
{
    __u64 skb = (__u64)ctx->skbaddr;
    __u64 now = bpf_ktime_get_ns();

    bpf_map_update_elem(&skb_timestamps, &skb, &now, BPF_ANY);
    return 0;
}

/* 2. Точка входу: вивільнення або успішна доставка в сокет */
SEC("tracepoint/skb/consume_skb")
int trace_consume_skb(struct trace_event_raw_consume_skb *ctx)
{
    __u64 skb = (__u64)ctx->skbaddr;
    __u64 *t_ingress = bpf_map_lookup_elem(&skb_timestamps, &skb);
    if (!t_ingress)
        return 0;

    __u64 now = bpf_ktime_get_ns();
    __u64 delta_us = (now - *t_ingress) / 1000;

    struct event_t *event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event) {
        bpf_map_delete_elem(&skb_timestamps, &skb);
        return 0;
    }

    event->skb_addr = skb;
    event->latency_total_us = delta_us;
    event->drop_reason = 0; /* 0 = успішна доставка */

    bpf_ringbuf_submit(event, 0);
    bpf_map_delete_elem(&skb_timestamps, &skb);
    return 0;
}

/* 3. Точка перехоплення: скидання пакета в ядрі */
SEC("tracepoint/skb/kfree_skb")
int trace_kfree_skb(struct trace_event_raw_kfree_skb *ctx)
{
    __u64 skb = (__u64)ctx->skbaddr;
    __u64 *t_ingress = bpf_map_lookup_elem(&skb_timestamps, &skb);
    __u64 now = bpf_ktime_get_ns();

    struct event_t *event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event) {
        if (t_ingress)
            bpf_map_delete_elem(&skb_timestamps, &skb);
        return 0;
    }

    event->skb_addr = skb;
    event->latency_total_us = t_ingress ? (now - *t_ingress) / 1000 : 0;
    event->drop_reason = ctx->reason;
    event->protocol = ctx->protocol;

    bpf_ringbuf_submit(event, 0);

    if (t_ingress)
        bpf_map_delete_elem(&skb_timestamps, &skb);
    return 0;
}
