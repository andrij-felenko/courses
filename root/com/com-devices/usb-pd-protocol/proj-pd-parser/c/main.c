#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PD_MAX_PAYLOAD_BYTES  260
#define PD_CRC_RESIDUE        0xC704DD7Bu

// Типи повідомлень USB PD (Control та Data)
typedef enum {
    PD_CTRL_GOOD_CRC       = 0x01,
    PD_CTRL_GOTO_MIN       = 0x02,
    PD_CTRL_ACCEPT         = 0x03,
    PD_CTRL_REJECT         = 0x04,
    PD_CTRL_PING           = 0x05,
    PD_CTRL_PS_RDY         = 0x06,
    PD_CTRL_GET_SRC_CAP    = 0x07,
    PD_CTRL_GET_SNK_CAP    = 0x08,
    PD_CTRL_DR_SWAP        = 0x09,
    PD_CTRL_PR_SWAP        = 0x0A,
    PD_CTRL_VCONN_SWAP     = 0x0B,
    PD_CTRL_WAIT           = 0x0C,
    PD_CTRL_SOFT_RESET     = 0x0D,
    PD_CTRL_NOT_SUPPORTED  = 0x10,

    PD_DATA_SRC_CAP        = 0x01,
    PD_DATA_REQUEST        = 0x02,
    PD_DATA_BIST           = 0x03,
    PD_DATA_SNK_CAP        = 0x04,
    PD_DATA_VDM            = 0x0F
} pd_msg_type_t;

// Структура розпарсеного основного заголовка
typedef struct {
    bool is_extended;
    uint8_t num_data_objects;
    uint8_t message_id;
    uint8_t power_role;       // 0 = Sink, 1 = Source
    uint8_t spec_rev;         // 2 = PD 3.0
    uint8_t data_role;        // 0 = UFP, 1 = DFP
    uint8_t msg_type;
} pd_header_t;

// Структура розширеного заголовка
typedef struct {
    bool chunked;
    uint8_t chunk_number;
    bool request_chunk;
    uint16_t data_size;
} pd_ext_header_t;

// Повний розпарсений пакет
typedef struct {
    pd_header_t header;
    pd_ext_header_t ext_header;
    const uint8_t *payload;
    uint16_t payload_len;
} pd_packet_t;

// Нібловий табличний розрахунок CRC-32 (IEEE 802.3 / USB PD)
static uint32_t pd_crc32_update(uint32_t crc, uint8_t byte) {
    static const uint32_t table[16] = {
        0x00000000, 0x1DB71064, 0x3B6E20C8, 0x26D930AC,
        0x76DC4190, 0x6B6B51F4, 0x4DB26158, 0x5005713C,
        0xEDB88320, 0xF00F9344, 0xD6D6A3E8, 0xCB61B38C,
        0x9B64C2B0, 0x86D3D2D4, 0xA00AE278, 0xBDBDF21C
    };
    uint8_t nibble;
    crc ^= byte;
    nibble = crc & 0x0F;
    crc = (crc >> 4) ^ table[nibble];
    nibble = (crc ^ (byte >> 4)) & 0x0F;
    crc = (crc >> 4) ^ table[nibble];
    return crc;
}

uint32_t pd_calculate_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; ++i) {
        crc = pd_crc32_update(crc, data[i]);
    }
    return ~crc;
}

// Парсер 16-бітного Message Header
static pd_header_t pd_parse_header(uint16_t raw_hdr) {
    pd_header_t h;
    h.msg_type         = (uint8_t)(raw_hdr & 0x1F);
    h.data_role        = (uint8_t)((raw_hdr >> 5) & 0x01);
    h.spec_rev         = (uint8_t)((raw_hdr >> 6) & 0x03);
    h.power_role       = (uint8_t)((raw_hdr >> 8) & 0x01);
    h.message_id       = (uint8_t)((raw_hdr >> 9) & 0x07);
    h.num_data_objects = (uint8_t)((raw_hdr >> 12) & 0x07);
    h.is_extended      = (bool)((raw_hdr >> 15) & 0x01);
    return h;
}

// Парсер 16-бітного Extended Message Header
static pd_ext_header_t pd_parse_ext_header(uint16_t raw_ext) {
    pd_ext_header_t eh;
    eh.data_size      = raw_ext & 0x01FF;
    eh.request_chunk  = (bool)((raw_ext >> 10) & 0x01);
    eh.chunk_number   = (uint8_t)((raw_ext >> 11) & 0x0F);
    eh.chunked        = (bool)((raw_ext >> 15) & 0x01);
    return eh;
}

// Головна функція валідації та парсингу
bool pd_parse_packet(const uint8_t *raw_buf, size_t total_len, pd_packet_t *out_pkt) {
    if (!raw_buf || total_len < 6 || !out_pkt) return false;

    // 1. Перевірка цілісності CRC-32
    size_t payload_and_hdr_len = total_len - 4;
    uint32_t calc_crc = pd_calculate_crc32(raw_buf, payload_and_hdr_len);
    uint32_t pkt_crc = (uint32_t)raw_buf[total_len - 4] |
                       ((uint32_t)raw_buf[total_len - 3] << 8) |
                       ((uint32_t)raw_buf[total_len - 2] << 16) |
                       ((uint32_t)raw_buf[total_len - 1] << 24);

    if (calc_crc != pkt_crc) {
        return false; // Збій контрольної суми
    }

    // 2. Декодування Message Header
    uint16_t raw_hdr = (uint16_t)raw_buf[0] | ((uint16_t)raw_buf[1] << 8);
    out_pkt->header = pd_parse_header(raw_hdr);

    // 3. Перевірка довжини корисного навантаження
    if (!out_pkt->header.is_extended) {
        size_t expected_len = (size_t)out_pkt->header.num_data_objects * 4;
        if (payload_and_hdr_len != 2 + expected_len) {
            return false; // Довжина не відповідає кількості об'єктів
        }
        out_pkt->payload = (expected_len > 0) ? &raw_buf[2] : NULL;
        out_pkt->payload_len = (uint16_t)expected_len;
        memset(&out_pkt->ext_header, 0, sizeof(out_pkt->ext_header));
    } else {
        if (payload_and_hdr_len < 4) return false;
        uint16_t raw_ext = (uint16_t)raw_buf[2] | ((uint16_t)raw_buf[3] << 8);
        out_pkt->ext_header = pd_parse_ext_header(raw_ext);
        out_pkt->payload = &raw_buf[4];
        out_pkt->payload_len = (uint16_t)(payload_and_hdr_len - 4);
    }

    return true;
}

// Генерація кадру GoodCRC у відповідь
size_t pd_build_goodcrc(uint8_t msg_id, uint8_t power_role, uint8_t data_role,
                        uint8_t spec_rev, uint8_t *out_buf, size_t max_buf_len) {
    if (!out_buf || max_buf_len < 6) return 0;

    // Керівне повідомлення GoodCRC: NumDataObjects = 0, MsgType = 0x01
    uint16_t hdr = (uint16_t)PD_CTRL_GOOD_CRC;
    hdr |= (uint16_t)(data_role & 0x01) << 5;
    hdr |= (uint16_t)(spec_rev & 0x03) << 6;
    hdr |= (uint16_t)(power_role & 0x01) << 8;
    hdr |= (uint16_t)(msg_id & 0x07) << 9;

    out_buf[0] = (uint8_t)(hdr & 0xFF);
    out_buf[1] = (uint8_t)((hdr >> 8) & 0xFF);

    uint32_t crc = pd_calculate_crc32(out_buf, 2);
    out_buf[2] = (uint8_t)(crc & 0xFF);
    out_buf[3] = (uint8_t)((crc >> 8) & 0xFF);
    out_buf[4] = (uint8_t)((crc >> 16) & 0xFF);
    out_buf[5] = (uint8_t)((crc >> 24) & 0xFF);

    return 6; // Фіксований розмір: 2 байти заголовка + 4 байти CRC
}
