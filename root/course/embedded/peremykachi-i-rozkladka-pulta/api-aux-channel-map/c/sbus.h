#ifndef SBUS_H
#define SBUS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "rc_channels.h"

/* Кадр SBUS: 25 байтів на UART 100 000 біт/с, 8E2, інвертований TTL.
   Інверсію знімає апаратний інвертор або біт CR2.RXINV — сюди байти
   приходять уже в прямій полярності. */

#define SBUS_FRAME_SIZE 25U
#define SBUS_HEADER     0x0FU
#define SBUS_FOOTER     0x00U
#define SBUS_FOOTER_V2  0x04U   /* Futaba S.BUS2 */

#define SBUS_FLAG_CH17       0x01U
#define SBUS_FLAG_CH18       0x02U
#define SBUS_FLAG_FRAME_LOST 0x04U
#define SBUS_FLAG_FAILSAFE   0x08U

typedef struct {
    uint16_t raw[RC_TOTAL_CHANNELS];
    bool ch17;        /* дискретний цифровий канал 17 */
    bool ch18;        /* дискретний цифровий канал 18 */
    bool frame_lost;  /* загублено окремий пакет */
    bool failsafe;    /* критична втрата лінку */
} sbus_frame_t;

typedef enum {
    SBUS_OK = 0,
    SBUS_ERR_ARGS,
    SBUS_ERR_SIZE,
    SBUS_ERR_HEADER,
    SBUS_ERR_FOOTER
} sbus_status_t;

sbus_status_t sbus_parse(const uint8_t *frame, size_t len, sbus_frame_t *out);
size_t sbus_build(const sbus_frame_t *in, uint8_t frame[SBUS_FRAME_SIZE]);
const char *sbus_status_text(sbus_status_t status);

#endif /* SBUS_H */
