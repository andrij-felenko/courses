#define FRAME_MAGIC        0xA55A
#define FRAME_HEADER_SIZE  6     // magic(2) + len(2) + type(1) + flags(1)
#define FRAME_MAX_PAYLOAD  128

typedef struct {
    uint16_t magic;
    uint16_t payload_len;
    uint8_t  type;
    uint8_t  flags;
    uint8_t  payload[FRAME_MAX_PAYLOAD];
    uint16_t crc;
} __attribute__((packed)) frame_t;

esp_err_t parse_packet(const uint8_t *buf, size_t len, frame_t *out) {
    // Застава 1: NULL-вказівник — інакше крах за нульовою адресою
    if (buf == NULL || out == NULL) {
        ESP_LOGE(TAG, "null ptr: buf=%p out=%p", buf, out);
        return ESP_ERR_INVALID_ARG;
    }

    // Застава 2: довжина хоча б на заголовок — інакше читання за межами
    if (len < FRAME_HEADER_SIZE) {
        ESP_LOGW(TAG, "frame too short: %zu < %d", len, FRAME_HEADER_SIZE);
        return ESP_ERR_INVALID_SIZE;
    }

    uint16_t magic       = (buf[0] << 8) | buf[1];
    uint16_t payload_len = (buf[2] << 8) | buf[3];

    // Застава 3: магічне число — інакше чужий або зашумований кадр
    if (magic != FRAME_MAGIC) {
        ESP_LOGW(TAG, "bad magic: 0x%04x", magic);
        return ESP_ERR_INVALID_RESPONSE;
    }

    // Застава 4: поле довжини в межах буфера — інакше читання за buf[len..]
    if (payload_len > FRAME_MAX_PAYLOAD ||
        len < FRAME_HEADER_SIZE + payload_len + 2 /* crc */) {
        ESP_LOGW(TAG, "len field out of bounds: %u", payload_len);
        return ESP_ERR_INVALID_SIZE;
    }

    // Застава 5: контрольна сума — інакше биті дані
    uint16_t recv_crc = (buf[FRAME_HEADER_SIZE + payload_len] << 8) |
                         buf[FRAME_HEADER_SIZE + payload_len + 1];
    uint16_t calc_crc = crc16(buf, FRAME_HEADER_SIZE + payload_len);
    if (recv_crc != calc_crc) {
        ESP_LOGW(TAG, "CRC mismatch: recv=0x%04x calc=0x%04x", recv_crc, calc_crc);
        return ESP_ERR_INVALID_CRC;
    }

    // Лише тепер дані довірені — читаємо навантаження
    out->magic       = magic;
    out->payload_len = payload_len;
    out->type        = buf[4];
    out->flags       = buf[5];
    memcpy(out->payload, buf + FRAME_HEADER_SIZE, payload_len);
    out->crc         = recv_crc;
    return ESP_OK;
}
