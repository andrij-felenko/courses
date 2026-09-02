#ifndef RC_CHANNELS_H
#define RC_CHANNELS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Спільне ядро радіотракту: числові діапазони, бітова упаковка 11-бітних
   каналів, розкладка каналів на осі, мертва зона й згладжування. */

#define RC_TOTAL_CHANNELS 16U
#define RC_PACKED_BYTES   22U   /* 16 каналів * 11 біт = 176 біт */

/* Розширений ШІМ-діапазон, у якому працюють цифрові протоколи */
#define RC_US_MIN     988U
#define RC_US_CENTER  1500U
#define RC_US_MAX     2012U

/* Відліки 11-бітного коду CRSF / SBUS */
#define RC_RAW_MIN    172U
#define RC_RAW_CENTER 992U
#define RC_RAW_MAX    1811U

/* Внутрішні осі польотного контролера — порядок НЕ залежить від протоколу */
typedef enum {
    RC_AXIS_ROLL = 0,
    RC_AXIS_PITCH,
    RC_AXIS_YAW,
    RC_AXIS_THROTTLE,
    RC_AXIS_COUNT
} rc_axis_t;

/* Порядок каналів на дроті: те, що в Betaflight задає `map`, а в ArduPilot —
   перелік RCMAP_ROLL / RCMAP_PITCH / RCMAP_THROTTLE / RCMAP_YAW */
typedef enum {
    RC_MAP_AETR = 0,   /* ExpressLRS, EdgeTX, Crossfire, Betaflight */
    RC_MAP_TAER,       /* Spektrum DSMX/DSM2, JR */
    RC_MAP_RETA,       /* FlySky i-BUS, класичний Futaba, Walkera */
    RC_MAP_ETAR,       /* Multiplex і європейські планерні системи */
    RC_MAP_COUNT
} rc_channel_map_t;

/* AUX1 — це CH5, тобто індекс 4 у нульовій нумерації */
#define RC_AUX_INDEX(n) ((uint8_t)((n) + 3U))

/* Перетворення за формулами розділу 3 (з округленням до найближчої мкс) */
uint16_t rc_raw_to_us(uint16_t raw);
uint16_t rc_us_to_raw(uint16_t us);

/* Бітова упаковка: 16 каналів по 11 біт, молодшим бітом уперед, без
   вирівнювання на байтові межі. Обидві функції — симетрична пара. */
void rc_unpack_11bit(const uint8_t payload[RC_PACKED_BYTES], uint16_t raw[RC_TOTAL_CHANNELS]);
void rc_pack_11bit(const uint16_t raw[RC_TOTAL_CHANNELS], uint8_t payload[RC_PACKED_BYTES]);

/* Індекс каналу, з якого дана розкладка бере дану вісь */
uint8_t rc_map_channel_index(rc_channel_map_t map, rc_axis_t axis);
const char *rc_map_name(rc_channel_map_t map);

/* Розкладання 16 каналів у чотири осі; false — невідома розкладка */
bool rc_apply_map(rc_channel_map_t map,
                  const uint16_t channels_us[RC_TOTAL_CHANNELS],
                  uint16_t axes_us[RC_AXIS_COUNT]);

/* Мертва зона довкола центру: у смузі повертає рівно центр, поза нею —
   зсунуте значення, щоб на межі не було стрибка (rc_deadband, rc_yaw_deadband) */
uint16_t rc_apply_deadband(uint16_t us, uint16_t deadband_us);

/* Біквадратний ФНЧ (rc_smoothing_cutoff): прибирає сходинки квантування
   пакетів між кадрами приймача */
typedef struct {
    float b0, b1, b2, a1, a2;
    float x1, x2, y1, y2;
    bool  primed;
} rc_biquad_t;

void  rc_biquad_init(rc_biquad_t *f, float cutoff_hz, float sample_hz);
float rc_biquad_apply(rc_biquad_t *f, float x);

#endif /* RC_CHANNELS_H */
