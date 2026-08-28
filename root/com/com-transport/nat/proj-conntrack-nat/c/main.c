#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define NAT_PORT_START 1024
#define NAT_PORT_END   65535
#define HASH_BUCKETS   4096
#define TCP_TIMEOUT_SEC 300
#define UDP_TIMEOUT_SEC 60

typedef struct {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint16_t src_port;
    uint16_t dst_port;
    uint8_t  proto;
} FlowTuple;

typedef struct NatEntry {
    FlowTuple original;      /* Прямий кортеж (LAN -> WAN) */
    FlowTuple reply;         /* Зворотний кортеж (WAN -> LAN) */
    uint16_t  assigned_port; /* Виділений WAN порт трансляції */
    time_t    last_seen;     /* Час останньої активності */
    struct NatEntry* next_orig;
    struct NatEntry* next_reply;
} NatEntry;

typedef struct {
    uint32_t wan_ip;
    NatEntry* orig_buckets[HASH_BUCKETS];
    NatEntry* reply_buckets[HASH_BUCKETS];
    bool port_allocated[NAT_PORT_END - NAT_PORT_START + 1];
    uint16_t next_port_scan;
} NatEngine;

/* Інкрементний перерахунок контрольної суми за RFC 1624 */
static inline uint16_t csum_update_u16(uint16_t old_csum, uint16_t old_val, uint16_t new_val) {
    uint32_t sum = (uint32_t)(~old_csum & 0xFFFF) + (uint32_t)(~old_val & 0xFFFF) + (uint32_t)new_val;
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return (uint16_t)(~sum & 0xFFFF);
}

static inline uint16_t csum_update_u32(uint16_t old_csum, uint32_t old_val, uint32_t new_val) {
    uint16_t old_hi = (uint16_t)(old_val >> 16);
    uint16_t old_lo = (uint16_t)(old_val & 0xFFFF);
    uint16_t new_hi = (uint16_t)(new_val >> 16);
    uint16_t new_lo = (uint16_t)(new_val & 0xFFFF);

    uint16_t c = csum_update_u16(old_csum, old_hi, new_hi);
    return csum_update_u16(c, old_lo, new_lo);
}

/* Хешування 5-компонентного кортежу */
static uint32_t hash_tuple(const FlowTuple* t) {
    uint32_t h = t->src_ip ^ t->dst_ip ^ ((uint32_t)t->src_port << 16 | t->dst_port) ^ t->proto;
    h ^= (h >> 16);
    return h % HASH_BUCKETS;
}

static bool tuple_equal(const FlowTuple* a, const FlowTuple* b) {
    return a->src_ip == b->src_ip && a->dst_ip == b->dst_ip &&
           a->src_port == b->src_port && a->dst_port == b->dst_port &&
           a->proto == b->proto;
}

/* Ініціалізація рушія NAT */
void nat_init(NatEngine* nat, uint32_t wan_ip) {
    nat->wan_ip = wan_ip;
    memset(nat->orig_buckets, 0, sizeof(nat->orig_buckets));
    memset(nat->reply_buckets, 0, sizeof(nat->reply_buckets));
    memset(nat->port_allocated, 0, sizeof(nat->port_allocated));
    nat->next_port_scan = 0;
}

/* Виділення ефемерного порту */
static int32_t allocate_port(NatEngine* nat) {
    uint16_t total = NAT_PORT_END - NAT_PORT_START + 1;
    for (uint16_t i = 0; i < total; ++i) {
        uint16_t idx = (nat->next_port_scan + i) % total;
        if (!nat->port_allocated[idx]) {
            nat->port_allocated[idx] = true;
            nat->next_port_scan = (idx + 1) % total;
            return NAT_PORT_START + idx;
        }
    }
    return -1; /* Пул портів вичерпано */
}

/* Обробка вихідного пакета LAN -> WAN (SNAT) */
bool nat_process_outbound(NatEngine* nat, uint8_t* pkt, uint32_t len, NatEntry* entry_pool, uint32_t* pool_idx, uint32_t max_entries) {
    if (len < 20) return false;
    uint8_t ihl = (pkt[0] & 0x0F) * 4;
    if (len < ihl + 8) return false;

    uint8_t proto = pkt[9];
    if (proto != 6 && proto != 17) return false;

    uint32_t src_ip = *(uint32_t*)&pkt[12];
    uint32_t dst_ip = *(uint32_t*)&pkt[16];
    uint16_t* src_port_ptr = (uint16_t*)&pkt[ihl];
    uint16_t* dst_port_ptr = (uint16_t*)&pkt[ihl + 2];
    uint16_t src_port = *src_port_ptr;
    uint16_t dst_port = *dst_port_ptr;

    FlowTuple key = { src_ip, dst_ip, src_port, dst_port, proto };
    uint32_t h = hash_tuple(&key);
    NatEntry* entry = nat->orig_buckets[h];

    while (entry) {
        if (tuple_equal(&entry->original, &key)) break;
        entry = entry->next_orig;
    }

    if (!entry) {
        if (*pool_idx >= max_entries) return false;
        int32_t port = allocate_port(nat);
        if (port < 0) return false;

        entry = &entry_pool[(*pool_idx)++];
        entry->original = key;
        entry->assigned_port = (uint16_t)port;
        entry->last_seen = time(NULL);

        /* Зворотний кортеж: WAN відповідь */
        entry->reply.src_ip = dst_ip;
        entry->reply.dst_ip = nat->wan_ip;
        entry->reply.src_port = dst_port;
        entry->reply.dst_port = (uint16_t)port;
        entry->reply.proto = proto;

        entry->next_orig = nat->orig_buckets[h];
        nat->orig_buckets[h] = entry;

        uint32_t rh = hash_tuple(&entry->reply);
        entry->next_reply = nat->reply_buckets[rh];
        nat->reply_buckets[rh] = entry;
    } else {
        entry->last_seen = time(NULL);
    }

    /* Модифікація IP-заголовка */
    uint16_t* ip_csum = (uint16_t*)&pkt[10];
    *ip_csum = csum_update_u32(*ip_csum, src_ip, nat->wan_ip);
    *(uint32_t*)&pkt[12] = nat->wan_ip;

    /* Модифікація L4-заголовка */
    uint16_t new_port = entry->assigned_port;
    if (proto == 6) { /* TCP */
        uint16_t* tcp_csum = (uint16_t*)&pkt[ihl + 16];
        uint16_t c = csum_update_u32(*tcp_csum, src_ip, nat->wan_ip);
        *tcp_csum = csum_update_u16(c, src_port, new_port);
    } else if (proto == 17) { /* UDP */
        uint16_t* udp_csum = (uint16_t*)&pkt[ihl + 6];
        if (*udp_csum != 0x0000) {
            uint16_t c = csum_update_u32(*udp_csum, src_ip, nat->wan_ip);
            c = csum_update_u16(c, src_port, new_port);
            *udp_csum = (c == 0x0000) ? 0xFFFF : c;
        }
    }
    *src_port_ptr = new_port;
    return true;
}

/* Обробка вхідного пакета WAN -> LAN (зворотний DNAT) */
bool nat_process_inbound(NatEngine* nat, uint8_t* pkt, uint32_t len) {
    if (len < 20) return false;
    uint8_t ihl = (pkt[0] & 0x0F) * 4;
    if (len < ihl + 8) return false;

    uint8_t proto = pkt[9];
    if (proto != 6 && proto != 17) return false;

    uint32_t src_ip = *(uint32_t*)&pkt[12];
    uint32_t dst_ip = *(uint32_t*)&pkt[16];
    uint16_t* src_port_ptr = (uint16_t*)&pkt[ihl];
    uint16_t* dst_port_ptr = (uint16_t*)&pkt[ihl + 2];
    uint16_t src_port = *src_port_ptr;
    uint16_t dst_port = *dst_port_ptr;

    FlowTuple key = { src_ip, dst_ip, src_port, dst_port, proto };
    uint32_t h = hash_tuple(&key);
    NatEntry* entry = nat->reply_buckets[h];

    while (entry) {
        if (tuple_equal(&entry->reply, &key)) break;
        entry = entry->next_reply;
    }

    if (!entry) {
        return false; /* Невідоме вхідне з'єднання: відкидаємо пакет */
    }

    entry->last_seen = time(NULL);
    uint32_t lan_ip = entry->original.src_ip;
    uint16_t lan_port = entry->original.src_port;

    /* Модифікація IP: Destination IP -> LAN IP */
    uint16_t* ip_csum = (uint16_t*)&pkt[10];
    *ip_csum = csum_update_u32(*ip_csum, dst_ip, lan_ip);
    *(uint32_t*)&pkt[16] = lan_ip;

    /* Модифікація L4: Destination Port -> LAN Port */
    if (proto == 6) {
        uint16_t* tcp_csum = (uint16_t*)&pkt[ihl + 16];
        uint16_t c = csum_update_u32(*tcp_csum, dst_ip, lan_ip);
        *tcp_csum = csum_update_u16(c, dst_port, lan_port);
    } else if (proto == 17) {
        uint16_t* udp_csum = (uint16_t*)&pkt[ihl + 6];
        if (*udp_csum != 0x0000) {
            uint16_t c = csum_update_u32(*udp_csum, dst_ip, lan_ip);
            c = csum_update_u16(c, dst_port, lan_port);
            *udp_csum = (c == 0x0000) ? 0xFFFF : c;
        }
    }
    *dst_port_ptr = lan_port;
    return true;
}
