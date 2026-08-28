/* ============================================================================
 * main_test.c — Тестування стійкості автомата до завад
 * ============================================================================ */
#include <stdio.h>
#include <assert.h>

int main(void) {
    parser_t parser;
    parser_init(&parser);

    uint8_t tx_buffer[128];
    uint8_t dummy_payload[4] = {0x11, 0x22, 0x33, 0x44};

    /* 1. Серіалізація тестового кадру */
    size_t frame_len = serialize_packet(0x02, 10, dummy_payload, 4, tx_buffer);
    assert(frame_len == 11);

    /* 2. Потокове декодування валідного кадру */
    packet_t rx_packet;
    parser_status_t status = PARSER_CONTINUE;
    for (size_t i = 0; i < frame_len; ++i) {
        status = parser_consume_byte(&parser, tx_buffer[i], &rx_packet);
    }
    assert(status == PARSER_PACKET_OK);
    assert(rx_packet.msg_id == 0x02);
    assert(rx_packet.seq == 10);
    assert(rx_packet.len == 4);

    /* 3. Симуляція пошкодження даних (Bit Flip) */
    tx_buffer[6] ^= 0x01; /* Спотворюємо один байт навантаження */
    for (size_t i = 0; i < frame_len; ++i) {
        status = parser_consume_byte(&parser, tx_buffer[i], &rx_packet);
    }
    assert(status == PARSER_ERR_CRC);

    /* 4. Симуляція випадання байта (Byte Slip) перед наступним нормальним пакетом */
    uint8_t stream_with_slip[25];
    /* Пакет 1 (битий, без 4-го байта) */
    memcpy(stream_with_slip, tx_buffer, 3);
    memcpy(stream_with_slip + 3, tx_buffer + 4, frame_len - 4);
    /* Пакет 2 (цілий) */
    size_t pkt2_len = serialize_packet(0x03, 11, dummy_payload, 4, stream_with_slip + frame_len - 1);

    int ok_packets = 0;
    for (size_t i = 0; i < (frame_len - 1 + pkt2_len); ++i) {
        status = parser_consume_byte(&parser, stream_with_slip[i], &rx_packet);
        if (status == PARSER_PACKET_OK) {
            ok_packets++;
        }
    }
    /* Перший пакет відкинуто через помилку довжини або CRC, другий успішно прийнято */
    assert(ok_packets == 1);
    assert(rx_packet.msg_id == 0x03);
    assert(rx_packet.seq == 11);

    return 0;
}
