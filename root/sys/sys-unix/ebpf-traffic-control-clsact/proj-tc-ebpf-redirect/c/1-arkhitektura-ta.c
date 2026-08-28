#include <linux/bpf.h>
#include <linux/pkt_cls.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <arpa/inet.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

#define TARGET_PORT 8080

// Конфігураційна карта BPF типу ARRAY для збереження індексу цільового інтерфейсу
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u32);
} config_map SEC(".maps");

SEC("classifier")
int tc_redirect_func(struct __sk_buff *skb) {
    // Зчитуємо межі лінійного буфера пакета з контексту skb
    void *data = (void *)(long)skb->data;
    void *data_end = (void *)(long)skb->data_end;

    // Крок 1: Перевірка меж та розпарсування Ethernet заголовка (L2)
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end) {
        return TC_ACT_OK; // Буфер надто малий — передаємо пакет далі
    }

    // Перевіряємо протокол L2: обробляємо лише кадри IPv4 (EtherType 0x0800)
    if (eth->h_proto != bpf_htons(ETH_P_IP)) {
        return TC_ACT_OK;
    }

    // Крок 2: Перевірка меж та розпарсування IP заголовка (L3)
    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end) {
        return TC_ACT_OK;
    }

    // Перевіряємо протокол L3: відфільтровуємо лише TCP-трафік (IPPROTO_TCP = 6)
    if (ip->protocol != IPPROTO_TCP) {
        return TC_ACT_OK;
    }

    // Крок 3: Перевірка меж та розпарсування TCP заголовка (L4)
    struct tcphdr *tcp = (void *)(ip + 1);
    if ((void *)(tcp + 1) > data_end) {
        return TC_ACT_OK;
    }

    // Крок 4: Аналіз порту призначення та прийняття рішення про перенаправлення
    if (tcp->dest == bpf_htons(TARGET_PORT)) {
        __u32 key = 0;
        __u32 *ifindex_ptr = bpf_map_lookup_elem(&config_map, &key);
        
        if (ifindex_ptr && *ifindex_ptr > 0) {
            // Перенаправляємо пакет на цільовий ifindex у режимі egress (flags = 0)
            return bpf_redirect(*ifindex_ptr, 0);
        }
    }

    // Усі інші пакети пропускаємо для стандартної обробки ядром
    return TC_ACT_OK;
}

char _license[] SEC("license") = "GPL";
