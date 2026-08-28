#include <stdio.h>

// Прикладна структура телеметрії
#pragma pack(push, 1)
typedef struct {
    float    battery_voltage;
    float    motor_current;
    int16_t  temperature_c;
} TelemetryPayload_t;
#pragma pack(pop)

static void handle_valid_frame(const FrameHeader_t *hdr, const uint8_t *payload, size_t len) {
    if (hdr->msg_id == 0x01 && len == sizeof(TelemetryPayload_t)) {
        const TelemetryPayload_t *telem = (const TelemetryPayload_t *)payload;
        printf("<- [RX OK] Seq=%u: V=%.2fV, I=%.2fA, T=%d C\n",
               hdr->seq_num, telem->battery_voltage, telem->motor_current, telem->temperature_c);
    }
}

// Пакування та кодування повного кадру в буфер передавача
size_t build_tx_frame(uint8_t msg_id, uint8_t seq, const void *payload, 
                      uint16_t payload_len, uint8_t *tx_out) 
{
    uint8_t raw_buffer[PROTOCOL_MAX_PACKET];
    FrameHeader_t *hdr = (FrameHeader_t *)raw_buffer;
    hdr->msg_id = msg_id;
    hdr->seq_num = seq;
    hdr->payload_len = payload_len;

    if (payload && payload_len > 0) {
        memcpy(raw_buffer + sizeof(FrameHeader_t), payload, payload_len);
    }

    size_t data_len = sizeof(FrameHeader_t) + payload_len;
    uint16_t crc = crc16_calculate(raw_buffer, data_len);
    raw_buffer[data_len++] = (uint8_t)(crc & 0xFF);
    raw_buffer[data_len++] = (uint8_t)((crc >> 8) & 0xFF);

    size_t encoded_len = cobs_encode(raw_buffer, data_len, tx_out);
    tx_out[encoded_len++] = 0x00; // Додаємо кінцевий розділювач кадру
    return encoded_len;
}

int main(void) {
    FramingParser_t parser;
    framing_parser_init(&parser, handle_valid_frame);

    TelemetryPayload_t telem_data = {
        .battery_voltage = 14.85f,
        .motor_current = 2.34f,
        .temperature_c = 42
    };

    uint8_t wire_bytes[PROTOCOL_MAX_ENCODED];
    size_t wire_len = build_tx_frame(0x01, 42, &telem_data, sizeof(telem_data), wire_bytes);

    printf("-> [TX] Сформовано кадр довжиною %zu байтів у лінії.\n", wire_len);

    // Симулюємо передачу: спочатку лінія дає сміття від брязкоту, потім іде кадр
    uint8_t glitch_noise[] = { 0xFF, 0x55, 0xAA, 0x00, 0x12, 0x00 };
    for (size_t i = 0; i < sizeof(glitch_noise); ++i) {
        framing_parser_feed_byte(&parser, glitch_noise[i]);
    }

    // Передаємо сам корисний кадр
    for (size_t i = 0; i < wire_len; ++i) {
        framing_parser_feed_byte(&parser, wire_bytes[i]);
    }

    printf("Підсумок парсера: прийнято=%u, помилок CRC=%u, переповнень=%u\n",
           parser.frames_received, parser.crc_errors, parser.overflow_errors);

    return 0;
}
