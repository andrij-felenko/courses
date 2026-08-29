#ifndef FM_MISSION_H
#define FM_MISSION_H

#include <stdbool.h>
#include <stdint.h>

#define FM_MISSION_MAX_ITEMS 64

/* Точка плану місії такою, якою її приймає бортовий буфер: координати в
   градусах, помножених на 1e7 (ціле, як у MAVLink), висота — відносна, метри. */
typedef struct {
    int32_t  lat_1e7;
    int32_t  lon_1e7;
    float    alt_rel_m;
    uint16_t command;   /* код навігаційної команди MAV_CMD */
} fm_mission_item_t;

typedef struct {
    fm_mission_item_t items[FM_MISSION_MAX_ITEMS];
    uint16_t count;
    uint16_t stored_crc;  /* контрольна сума, надіслана наземною станцією */
} fm_mission_t;

typedef enum {
    FM_MISSION_OK = 0,
    FM_MISSION_EMPTY,
    FM_MISSION_CRC_MISMATCH,
    FM_MISSION_BAD_ALTITUDE,
    FM_MISSION_OUT_OF_FENCE,
    FM_MISSION_BAD_COMMAND
} fm_mission_status_t;

void fm_mission_clear(fm_mission_t *m);

/* Додає точку в буфер; false — буфер повний. Після наповнення станція надсилає
   свою контрольну суму, і план вважається прийнятим лише після звіряння. */
bool fm_mission_append(fm_mission_t *m, const fm_mission_item_t *item);

/* CRC-16/CCITT-FALSE по значущих полях точок — тим самим поліномом, яким
   MAVLink підписує переданий план. */
uint16_t fm_mission_crc(const fm_mission_t *m);

/* Повна валідація плану: непорожній, контрольна сума збігається, висоти в межах
   стелі, усі точки — в дозволеному радіусі від точки старту. */
fm_mission_status_t fm_mission_validate(const fm_mission_t *m,
                                        int32_t home_lat_1e7, int32_t home_lon_1e7,
                                        float fence_radius_m, float max_alt_m);

const char *fm_mission_status_text(fm_mission_status_t st);

/* Зміщення точки B відносно A в місцевій системі Північ-Схід, метри (плоска
   апроксимація — на масштабах геозони похибка менша за метр). */
void fm_geo_offset_m(int32_t lat_a_1e7, int32_t lon_a_1e7,
                     int32_t lat_b_1e7, int32_t lon_b_1e7,
                     float *north_m, float *east_m);

/* Горизонтальна відстань між двома координатами, метри. */
float fm_geo_distance_m(int32_t lat_a_1e7, int32_t lon_a_1e7,
                        int32_t lat_b_1e7, int32_t lon_b_1e7);

#endif /* FM_MISSION_H */
