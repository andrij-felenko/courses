// cgroup_fw.bpf.c — Ядерна eBPF-програма фільтрації cgroup
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

// BPF Map (хеш-таблиця) для збереження заблокованих IPv4-адрес.
// Ключ — 32-бітна IPv4 адреса у мережевому порядку байтів.
// Значення — 64-бітний лічильник заблокованих пакетів.
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);   // IPv4 адреса (Big-Endian)
    __type(value, __u64); // Лічильник скинутих пакетів
} blocklist SEC(".maps");

SEC("cgroup_skb/egress")
int cgroup_egress_firewall(struct __sk_buff *skb)
{
    // 1. Перевіряємо мережевий протокол. Пропускаємо пакети, які не є IPv4.
    // Значення skb->protocol знаходиться у мережевому порядку байтів (Big-Endian).
    if (skb->protocol != bpf_htons(ETH_P_IP)) {
        return 1; // 1 = Дозволити передачу пакета
    }

    // 2. Безпечно читаємо IP-заголовок з пакета.
    // На хуку cgroup egress пакет не має Ethernet-заголовка, skb->data вказує на IP-заголовок.
    struct iphdr iph;
    if (bpf_skb_load_bytes(skb, 0, &iph, sizeof(iph)) < 0) {
        return 1; // У разі помилки читання не блокуємо трафік
    }

    __u32 dest_ip = iph.daddr;

    // 3. Шукаємо IP-адресу призначення у хеш-мапі заблокованих адрес
    __u64 *drop_count = bpf_map_lookup_elem(&blocklist, &dest_ip);
    if (drop_count) {
        // Атомарно збільшуємо лічильник заблокованих пакетів для цієї адреси
        __sync_fetch_and_add(drop_count, 1);

        // Записуємо інформаційне повідомлення у відлагоджувальний буфер ядра
        bpf_printk("cgroup_fw: BLOCKED egress packet to IP %x\n", bpf_ntohl(dest_ip));

        // Повертаємо 0 -> Ядро негайно відкидає пакет і повертає EPERM
        return 0;
    }

    // 4. IP-адреса відсутня у списку блокування — дозволяємо пакет
    return 1;
}

char _license[] SEC("license") = "GPL";
