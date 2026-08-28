#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define DVP_CHUNK_PAYLOAD_MAX  1400
#define DVP_DMA_BUFFER_SIZE    2048
#define DVP_PROTO_MAGIC        0x56494445U /* "VIDE" ASCII */

#define FLAG_FIRST_CHUNK       (1U << 0)
#define FLAG_LAST_CHUNK        (1U << 1)

#define JPEG_MARKER_PREFIX     0xFFU
#define JPEG_MARKER_SOI        0xD8U
#define JPEG_MARKER_EOI        0xD9U

/* Заголовок мережевого пакета кадру */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t frame_id;
    uint16_t chunk_idx;
    uint16_t payload_len;
    uint16_t flags;
    uint32_t crc32;
} frame_packet_header_t;

/* Транспортний пакет для передачі у мережу */
typedef struct {
    frame_packet_header_t header;
    uint8_t payload[DVP_CHUNK_PAYLOAD_MAX];
} frame_packet_t;

/* Стани скінченного автомата розбору потоку */
typedef enum {
    FSM_STATE_SEARCH_SOI = 0,
    FSM_STATE_STREAM_PAYLOAD,
    FSM_STATE_FRAME_COMPLETE
} fsm_state_t;

/* Статистика та лічильники драйвера */
typedef struct {
    uint32_t frames_captured;
    uint32_t frames_dropped;
    uint32_t bytes_processed;
    uint32_t chunks_transmitted;
} stream_stats_t;

/* Контекст потокового детектора */
typedef struct {
    fsm_state_t state;
    uint16_t current_frame_id;
    uint16_t current_chunk_idx;
    bool prev_byte_was_ff;
    frame_packet_t tx_packet;
    stream_stats_t stats;
} dvp_stream_parser_t;

/* Табличний розрахунок контрольної суми CRC32 (IEEE 802.3) */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint32_t)data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(uint32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

/* Ініціалізація структури парсера */
void dvp_parser_init(dvp_stream_parser_t *parser) {
    if (!parser) return;
    memset(parser, 0, sizeof(dvp_stream_parser_t));
    parser->state = FSM_STATE_SEARCH_SOI;
    parser->current_frame_id = 1;
}

/* Зовнішня функція відправки зібраного пакета в мережевий сокет або радіолінк */
extern bool network_send_packet(const frame_packet_t *pkt, size_t total_len);

/* Відправка наповненого чанка */
static void flush_tx_chunk(dvp_stream_parser_t *parser, bool is_last) {
    if (parser->tx_packet.header.payload_len == 0 && !is_last) {
        return;
    }

    parser->tx_packet.header.magic = DVP_PROTO_MAGIC;
    parser->tx_packet.header.frame_id = parser->current_frame_id;
    parser->tx_packet.header.chunk_idx = parser->current_chunk_idx;
    
    uint16_t flags = 0;
    if (parser->current_chunk_idx == 0) {
        flags |= FLAG_FIRST_CHUNK;
    }
    if (is_last) {
        flags |= FLAG_LAST_CHUNK;
    }
    parser->tx_packet.header.flags = flags;

    /* Розрахунок CRC32 корисного навантаження */
    parser->tx_packet.header.crc32 = calculate_crc32(
        parser->tx_packet.payload, 
        parser->tx_packet.header.payload_len
    );

    size_t packet_size = sizeof(frame_packet_header_t) + parser->tx_packet.header.payload_len;
    network_send_packet(&parser->tx_packet, packet_size);

    parser->stats.chunks_transmitted++;
    parser->current_chunk_idx++;
    parser->tx_packet.header.payload_len = 0;
}

/* Потокова обробка сирого буфера, отриманого від DMA контролера */
void dvp_process_dma_buffer(dvp_stream_parser_t *parser, const uint8_t *dma_buf, size_t len) {
    if (!parser || !dma_buf || len == 0) return;

    for (size_t i = 0; i < len; ++i) {
        uint8_t byte = dma_buf[i];
        parser->stats.bytes_processed++;

        switch (parser->state) {
            case FSM_STATE_SEARCH_SOI:
                if (parser->prev_byte_was_ff && byte == JPEG_MARKER_SOI) {
                    /* Знайдено SOI маркер: записуємо FF D8 у початок пакета */
                    parser->state = FSM_STATE_STREAM_PAYLOAD;
                    parser->current_chunk_idx = 0;
                    parser->tx_packet.payload[0] = JPEG_MARKER_PREFIX;
                    parser->tx_packet.payload[1] = JPEG_MARKER_SOI;
                    parser->tx_packet.header.payload_len = 2;
                    parser->prev_byte_was_ff = false;
                } else {
                    parser->prev_byte_was_ff = (byte == JPEG_MARKER_PREFIX);
                }
                break;

            case FSM_STATE_STREAM_PAYLOAD:
                /* Перевірка на EOI маркер */
                if (parser->prev_byte_was_ff && byte == JPEG_MARKER_EOI) {
                    /* Дописуємо закриваючий байт D9 */
                    if (parser->tx_packet.header.payload_len < DVP_CHUNK_PAYLOAD_MAX) {
                        parser->tx_packet.payload[parser->tx_packet.header.payload_len++] = byte;
                    }
                    /* Відправляємо фінальний чанк кадру */
                    flush_tx_chunk(parser, true);
                    
                    parser->stats.frames_captured++;
                    parser->current_frame_id++;
                    parser->state = FSM_STATE_SEARCH_SOI;
                    parser->prev_byte_was_ff = false;
                    break;
                }

                /* Запис поточного байта у вихідний буфер */
                parser->tx_packet.payload[parser->tx_packet.header.payload_len++] = byte;
                parser->prev_byte_was_ff = (byte == JPEG_MARKER_PREFIX);

                /* Якщо чанк наповнився до ліміту MTU — транслюємо його */
                if (parser->tx_packet.header.payload_len >= DVP_CHUNK_PAYLOAD_MAX) {
                    flush_tx_chunk(parser, false);
                }
                break;

            case FSM_STATE_FRAME_COMPLETE:
                parser->state = FSM_STATE_SEARCH_SOI;
                parser->prev_byte_was_ff = false;
                break;
        }
    }
}
