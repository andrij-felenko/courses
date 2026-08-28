#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define PBCAST_BUFFER_CAPACITY 1024
#define PBCAST_MAX_PAYLOAD 512
#define PBCAST_MASK_BITS 64

/* Структура збереженого пакета в кільцевому буфері */
typedef struct {
    uint64_t seq_num;
    uint32_t payload_len;
    uint8_t  payload[PBCAST_MAX_PAYLOAD];
    bool     valid;
} pbcast_slot_t;

/* Кільцевий буфер для одного джерела мовлення */
typedef struct {
    uint64_t      sender_id;
    uint64_t      low_watermark;
    uint64_t      received_mask;
    pbcast_slot_t slots[PBCAST_BUFFER_CAPACITY];
} pbcast_buffer_t;

/* Ініціалізація буфера джерела */
void pbcast_buffer_init(pbcast_buffer_t *buf, uint64_t sender_id, uint64_t initial_seq) {
    buf->sender_id = sender_id;
    buf->low_watermark = initial_seq;
    buf->received_mask = 0;
    for (size_t i = 0; i < PBCAST_BUFFER_CAPACITY; ++i) {
        buf->slots[i].valid = false;
        buf->slots[i].seq_num = 0;
        buf->slots[i].payload_len = 0;
    }
}
