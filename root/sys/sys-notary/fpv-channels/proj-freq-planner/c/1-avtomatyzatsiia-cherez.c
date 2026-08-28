#include <stdint.h>

/* Структура бінарного пакета MSP_SET_VTX_CONFIG (10 байтів) */
typedef struct __attribute__((packed)) {
    uint8_t  vtx_type;         /* 1 = SmartAudio, 2 = Tramp */
    uint16_t frequency_mhz;    /* Несуча частота (наприклад, 5658) */
    uint8_t  power_level;      /* Індекс рівня потужності (1..5) */
    uint8_t  pit_mode;         /* 0 = Off, 1 = On */
    uint8_t  band;             /* Номер смуги (1..6) */
    uint8_t  channel;          /* Номер каналу (1..8) */
} MspVtxConfigPayload;
