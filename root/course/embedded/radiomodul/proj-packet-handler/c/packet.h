#ifndef PACKET_H
#define PACKET_H

#include <stddef.h>
#include <stdint.h>

#define PREAMBLE_BYTE 0xAAu /* 10101010 — суцільне чергування фронтів */
#define PREAMBLE_LEN  4     /* байтів на розгін AGC і бітового ФАПЧ */
#define SYNC_WORD     0xD391u /* синхрослово CC1101, у ефір старшим байтом уперед */
#define SYNC_MASK     0xFFFFu /* 16 бітів корелятора */

#define PACKET_MAX_PAYLOAD 64
/* преамбула + синхрослово + довжина + дані + CRC */
#define PACKET_MAX_FRAME (PREAMBLE_LEN + 2 + 1 + PACKET_MAX_PAYLOAD + 2)

typedef struct {
    uint8_t data[PACKET_MAX_PAYLOAD];
    uint8_t len;
} packet_t;

/* Збирає кадр в ефірному вигляді. Повертає довжину кадру або 0, якщо
   payload порожній, задовгий чи вихідний буфер малий. */
size_t packet_build(const uint8_t *payload, uint8_t len,
                    uint8_t *frame_out, size_t frame_cap);

#endif /* PACKET_H */
