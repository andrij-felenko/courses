#include <stdint.h>
#include <stdbool.h>

#define ETH_ALEN         6
#define ETH_HLEN         14
#define ETH_ZLEN         60
#define ETH_DATA_LEN     1500
#define ETH_FRAME_LEN    1514
#define ETH_FCS_LEN      4

/* Константи EtherType */
#define ETHERTYPE_IPV4       0x0800
#define ETHERTYPE_ARP        0x0806
#define ETHERTYPE_VLAN       0x8100
#define ETHERTYPE_IPV6       0x86DD
#define ETHERTYPE_QINQ       0x88A8
#define ETHERTYPE_LLDP       0x88CC
#define ETHERTYPE_PTP        0x88F7

/* Заголовок Ethernet II (14 байтів) */
#pragma pack(push, 1)
struct eth_hdr {
    uint8_t  dst_mac[ETH_ALEN];
    uint8_t  src_mac[ETH_ALEN];
    uint16_t ethertype;          /* Передається у Big-Endian */
};

/* 4-байтовий тег IEEE 802.1Q */
struct vlan_hdr {
    uint16_t tpid;               /* 0x8100 або 0x88A8 */
    uint16_t tci;                /* PCP (3 біти), DEI (1 біт), VID (12 бітів) */
};

/* Заголовок IEEE 802.3 LLC/SNAP */
struct ieee8023_llc_snap_hdr {
    uint8_t  dst_mac[ETH_ALEN];
    uint8_t  src_mac[ETH_ALEN];
    uint16_t length;             /* Довжина <= 1500 */
    uint8_t  dsap;               /* 0xAA */
    uint8_t  ssap;               /* 0xAA */
    uint8_t  control;            /* 0x03 */
    uint8_t  oui[3];             /* 0x000000 */
    uint16_t ethertype;          /* Big-Endian код протоколу */
};
#pragma pack(pop)

/* Допоміжні функції аналізу бітових прапорів */
static inline bool eth_is_multicast(const uint8_t *mac) {
    return (mac[0] & 0x01) != 0;
}

static inline bool eth_is_broadcast(const uint8_t *mac) {
    return (mac[0] == 0xFF && mac[1] == 0xFF && mac[2] == 0xFF &&
            mac[3] == 0xFF && mac[4] == 0xFF && mac[5] == 0xFF);
}

static inline bool eth_is_local_admin(const uint8_t *mac) {
    return (mac[0] & 0x02) != 0;
}

static inline uint8_t vlan_get_pcp(uint16_t tci_host_order) {
    return (uint8_t)((tci_host_order >> 13) & 0x07);
}

static inline bool vlan_get_dei(uint16_t tci_host_order) {
    return (bool)((tci_host_order >> 12) & 0x01);
}

static inline uint16_t vlan_get_vid(uint16_t tci_host_order) {
    return (tci_host_order & 0x0FFF);
}
