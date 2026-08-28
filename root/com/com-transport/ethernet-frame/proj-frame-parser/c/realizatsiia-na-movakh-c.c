#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ETH_ALEN           6
#define ETH_MIN_LEN        60
#define ETH_MAX_LEN        1514
#define ETHERTYPE_VLAN     0x8100
#define ETHERTYPE_QINQ     0x88A8

/* Структура результату розбору кадру */
typedef struct {
    uint8_t  dst_mac[ETH_ALEN];
    uint8_t  src_mac[ETH_ALEN];
    uint16_t vlan_ids[2];       /* Підтримка до 2 вкладених тегів (QinQ) */
    uint8_t  vlan_pcp[2];
    uint8_t  vlan_count;
    uint16_t ethertype;         /* Підсумковий EtherType після зняття тегів */
    const uint8_t *payload;     /* Вказівник на початок корисних даних */
    size_t   payload_len;       /* Довжина корисних даних */
    bool     fcs_valid;         /* Результат перевірки CRC-32 */
} parsed_frame_t;

/* Таблиця для швидкого розрахунку CRC-32 IEEE 802.3 */
static uint32_t crc32_table[256];
static bool crc32_table_ready = false;

static void init_crc32_table(void) {
    const uint32_t polynomial = 0xEDB88320u;
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t crc = i;
        for (int j = 0; j < 8; ++j) {
            if (crc & 1)
                crc = (crc >> 1) ^ polynomial;
            else
                crc >>= 1;
        }
        crc32_table[i] = crc;
    }
    crc32_table_ready = true;
}

uint32_t ethernet_crc32(const uint8_t *data, size_t len) {
    if (!crc32_table_ready)
        init_crc32_table();

    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; ++i) {
        uint8_t table_idx = (uint8_t)((crc ^ data[i]) & 0xFF);
        crc = (crc >> 8) ^ crc32_table[table_idx];
    }
    return crc ^ 0xFFFFFFFFu;
}

/* Безпечний парсер Ethernet-кадру */
int parse_ethernet_frame(const uint8_t *raw_buf, size_t buf_len,
                         bool has_fcs, parsed_frame_t *out) {
    if (!raw_buf || !out || buf_len < 14)
        return -1; /* Помилка: буфер замалий для мінімального заголовка */

    memset(out, 0, sizeof(*out));
    memcpy(out->dst_mac, raw_buf, ETH_ALEN);
    memcpy(out->src_mac, raw_buf + ETH_ALEN, ETH_ALEN);

    size_t offset = 12;
    out->vlan_count = 0;

    /* Зчитуємо та знімаємо теги VLAN (до 2 рівнів) */
    while (offset + 4 <= buf_len && out->vlan_count < 2) {
        uint16_t tag_type = (uint16_t)((raw_buf[offset] << 8) | raw_buf[offset + 1]);
        if (tag_type != ETHERTYPE_VLAN && tag_type != ETHERTYPE_QINQ)
            break;

        uint16_t tci = (uint16_t)((raw_buf[offset + 2] << 8) | raw_buf[offset + 3]);
        out->vlan_pcp[out->vlan_count] = (uint8_t)((tci >> 13) & 0x07);
        out->vlan_ids[out->vlan_count] = (uint16_t)(tci & 0x0FFF);
        out->vlan_count++;
        offset += 4;
    }

    if (offset + 2 > buf_len)
        return -2; /* Обрізаний заголовок після тегів VLAN */

    out->ethertype = (uint16_t)((raw_buf[offset] << 8) | raw_buf[offset + 1]);
    offset += 2;

    /* Перевірка формату IEEE 802.3 LLC/SNAP */
    if (out->ethertype <= 1500) {
        if (offset + 8 <= buf_len &&
            raw_buf[offset] == 0xAA && raw_buf[offset + 1] == 0xAA && raw_buf[offset + 2] == 0x03) {
            /* SNAP Header знайдено */
            out->ethertype = (uint16_t)((raw_buf[offset + 6] << 8) | raw_buf[offset + 7]);
            offset += 8;
        }
    }

    size_t data_end = buf_len;
    if (has_fcs) {
        if (buf_len < offset + 4)
            return -3; /* Буфер не містить 4 байтів FCS */
        data_end -= 4;

        uint32_t expected_crc = ethernet_crc32(raw_buf, data_end);
        uint32_t actual_crc = (uint32_t)raw_buf[data_end] |
                             ((uint32_t)raw_buf[data_end + 1] << 8) |
                             ((uint32_t)raw_buf[data_end + 2] << 16) |
                             ((uint32_t)raw_buf[data_end + 3] << 24);
        out->fcs_valid = (expected_crc == actual_crc);
    } else {
        out->fcs_valid = true; /* Апаратне розвантаження підтвердило цілісність */
    }

    out->payload = raw_buf + offset;
    out->payload_len = data_end - offset;
    return 0;
}
