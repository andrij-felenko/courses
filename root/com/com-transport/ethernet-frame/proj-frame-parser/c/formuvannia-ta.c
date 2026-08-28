#include <stdint.h>
#include <string.h>
#include <arpa/inet.h>

size_t craft_ethernet_frame(const uint8_t *dst_mac, const uint8_t *src_mac,
                            uint16_t vlan_id, uint16_t ethertype,
                            const uint8_t *payload, size_t payload_len,
                            uint8_t *out_buf, size_t max_buf_len) {
    size_t offset = 0;

    /* Копіюємо MAC-адреси */
    memcpy(out_buf + offset, dst_mac, 6); offset += 6;
    memcpy(out_buf + offset, src_mac, 6); offset += 6;

    /* Якщо вказано VLAN ID (1..4094), вставляємо тег 802.1Q */
    if (vlan_id >= 1 && vlan_id <= 4094) {
        out_buf[offset++] = 0x81;
        out_buf[offset++] = 0x00;
        uint16_t tci = htons(vlan_id & 0x0FFF);
        memcpy(out_buf + offset, &tci, 2); offset += 2;
    }

    /* Записуємо EtherType */
    uint16_t etype_be = htons(ethertype);
    memcpy(out_buf + offset, &etype_be, 2); offset += 2;

    /* Копіюємо дані */
    memcpy(out_buf + offset, payload, payload_len);
    offset += payload_len;

    /* Доповнюємо нулями до мінімального розміру 60 байтів (без FCS) */
    if (offset < 60) {
        memset(out_buf + offset, 0, 60 - offset);
        offset = 60;
    }

    /* Обчислюємо та дописуємо FCS CRC-32 */
    uint32_t crc = ethernet_crc32(out_buf, offset);
    out_buf[offset++] = (uint8_t)(crc & 0xFF);
    out_buf[offset++] = (uint8_t)((crc >> 8) & 0xFF);
    out_buf[offset++] = (uint8_t)((crc >> 16) & 0xFF);
    out_buf[offset++] = (uint8_t)((crc >> 24) & 0xFF);

    return offset;
}
