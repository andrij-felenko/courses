#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RC_CHANNEL_MIN_US    988U
#define RC_CHANNEL_MAX_US    2012U
#define RC_CHANNEL_CENTER_US 1500U
#define RC_TOTAL_CHANNELS    16U

/* Порядок каналів керування */
typedef enum {
    RC_MAP_AETR = 0,
    RC_MAP_TAER = 1,
    RC_MAP_RETA = 2
} rc_channel_map_t;

/* Дискретні позиції перемикачів */
typedef enum {
    SWITCH_POS_LOW    = 0,
    SWITCH_POS_CENTER = 1,
    SWITCH_POS_HIGH   = 2
} switch_position_t;

/* Структура декодованого стану радіоканалу */
typedef struct {
    uint16_t raw_us;            /* Сире значення в мікросекундах */
    switch_position_t state;    /* Дискретний стан перемикача */
    bool is_valid;              /* Прапорець достовірності сигналу */
} rc_aux_channel_t;

/* Розпакування 16 11-бітних каналів з 22-байтового буфера */
void rc_unpack_11bit_channels(const uint8_t *payload, uint16_t *channels_us) {
    if (payload == NULL || channels_us == NULL) {
        return;
    }

    uint16_t raw[RC_TOTAL_CHANNELS];

    raw[0]  = (uint16_t)((payload[0]       | (payload[1] << 8))                      & 0x07FF);
    raw[1]  = (uint16_t)(((payload[1] >> 3) | (payload[2] << 5))                      & 0x07FF);
    raw[2]  = (uint16_t)(((payload[2] >> 6) | (payload[3] << 2) | (payload[4] << 10)) & 0x07FF);
    raw[3]  = (uint16_t)(((payload[4] >> 1) | (payload[5] << 7))                      & 0x07FF);
    raw[4]  = (uint16_t)(((payload[5] >> 4) | (payload[6] << 4))                      & 0x07FF);
    raw[5]  = (uint16_t)(((payload[6] >> 7) | (payload[7] << 1) | (payload[8] << 9))  & 0x07FF);
    raw[6]  = (uint16_t)(((payload[8] >> 2) | (payload[9] << 6))                      & 0x07FF);
    raw[7]  = (uint16_t)(((payload[9] >> 5) | (payload[10] << 3))                     & 0x07FF);
    raw[8]  = (uint16_t)((payload[11]      | (payload[12] << 8))                     & 0x07FF);
    raw[9]  = (uint16_t)(((payload[12] >> 3)| (payload[13] << 5))                     & 0x07FF);
    raw[10] = (uint16_t)(((payload[13] >> 6)| (payload[14] << 2)| (payload[15] << 10))& 0x07FF);
    raw[11] = (uint16_t)(((payload[15] >> 1)| (payload[16] << 7))                     & 0x07FF);
    raw[12] = (uint16_t)(((payload[16] >> 4)| (payload[17] << 4))                     & 0x07FF);
    raw[13] = (uint16_t)(((payload[17] >> 7)| (payload[18] << 1)| (payload[19] << 9)) & 0x07FF);
    raw[14] = (uint16_t)(((payload[19] >> 2)| (payload[20] << 6))                     & 0x07FF);
    raw[15] = (uint16_t)(((payload[20] >> 5)| (payload[21] << 3))                     & 0x07FF);

    for (uint8_t i = 0; i < RC_TOTAL_CHANNELS; ++i) {
        /* Масштабування відліку 172..1811 у мікросекунди 988..2012 */
        if (raw[i] < 172U) {
            channels_us[i] = RC_CHANNEL_MIN_US;
        } else if (raw[i] > 1811U) {
            channels_us[i] = RC_CHANNEL_MAX_US;
        } else {
            channels_us[i] = (uint16_t)(988U + (((uint32_t)(raw[i] - 172U) * 1024U) / 1640U));
        }
    }
}
