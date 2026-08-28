#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "shared_tree.h"

char _license[] SEC("license") = "GPL";

struct {
    __uint(type, BPF_MAP_TYPE_ARENA);
    __uint(map_flags, BPF_F_MMAPABLE);
    __uint(max_entries, 1024); /* 1024 сторінки = 4 МБ */
} arena_map SEC(".maps");

SEC("tc")
int filter_traffic(struct __sk_buff *skb)
{
    void *data = (void *)(long)skb->data;
    void *data_end = (void *)(long)skb->data_end;

    /* Минімальна перевірка кордонів буфера Ethernet-заголовка */
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return TC_ACT_OK;

    if (eth->h_proto != bpf_htons(ETH_P_IP))
        return TC_ACT_OK;

    /* Перевірка кордонів IP-заголовка */
    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end)
        return TC_ACT_OK;

    uint32_t dst_ip = bpf_ntohl(ip->daddr);

    /* Отримання базової адреси заголовка арени */
    struct arena_root_header __arena *hdr = (struct arena_root_header __arena *)bpf_map_lookup_elem(&arena_map, &(uint32_t){0});
    if (!hdr || hdr->magic != ARENA_MAGIC)
        return TC_ACT_OK;

    __sync_fetch_and_add(&hdr->total_lookups, 1);

    /* Прямий обхід дерева за C-вказівниками у спільній пам'яті */
    struct radix_node __arena *curr = hdr->root;
    int action = TC_ACT_OK;

    while (curr) {
        if (curr->action == 1) {
            action = TC_ACT_SHOT; /* Блокування пакета */
            __sync_fetch_and_add(&hdr->total_matches, 1);
            break;
        }

        /* Обчислення біта за довжиною префікса */
        uint32_t bit_idx = 31 - curr->prefix_len;
        uint32_t bit = (dst_ip >> bit_idx) & 1;

        curr = curr->child[bit];
    }

    return action;
}
