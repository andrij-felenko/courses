#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ETH_ALEN       6
#define ETH_HLEN       14
#define ETHERTYPE_IPV4 0x0800
#define ETHERTYPE_VLAN 0x8100

struct eth_header {
    uint8_t  dst[ETH_ALEN];
    uint8_t  src[ETH_ALEN];
    uint16_t type; /* У Big-Endian порядку */
};

/* Базова перевірка та виділення EtherType */
bool parse_ethernet_header(const uint8_t *buffer, size_t len,
                           uint16_t *out_ethertype, size_t *out_payload_offset) {
    if (len < ETH_HLEN)
        return false;

    size_t offset = 12;
    uint16_t proto = (uint16_t)((buffer[offset] << 8) | buffer[offset + 1]);
    offset += 2;

    /* Обробка тега 802.1Q */
    if (proto == ETHERTYPE_VLAN) {
        if (len < offset + 4)
            return false;
        /* Пропускаємо TCI (2 байти) і читаємо справжній EtherType */
        offset += 2;
        proto = (uint16_t)((buffer[offset] << 8) | buffer[offset + 1]);
        offset += 2;
    }

    *out_ethertype = proto;
    *out_payload_offset = offset;
    return true;
}
