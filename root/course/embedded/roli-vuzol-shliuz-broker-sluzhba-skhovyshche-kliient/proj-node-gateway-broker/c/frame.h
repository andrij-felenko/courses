/* frame.h — контракт бінарного кадру каналу «вузол ↔ шлюз».
 *
 * Усі три типи кадру мають однакову довжину 16 байтів: так приймачу
 * достатньо одного правила кадрування (магія + 15 байтів + CRC) в обидва боки.
 */
#ifndef FRAME_H
#define FRAME_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Порядок байтів на дроті зафіксовано контрактом: little-endian.
   Cortex-M і x86 такі й є; на big-endian хості код не збереться навмисно —
   мовчазне спотворення node_id гірше за помилку компіляції. */
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "Кадр зафіксовано little-endian; для big-endian хоста потрібна явна конверсія полів"
#endif

#define FRAME_MAGIC 0xAAu
#define FRAME_SIZE  16u

enum frame_type {
    FRAME_TYPE_TELEMETRY = 0x01,
    FRAME_TYPE_COMMAND   = 0x02,
    FRAME_TYPE_ACK       = 0x03
};

enum command_id {
    CMD_SET_RELAY = 0x10
};

enum ack_status {
    ACK_OK          = 0x00,
    ACK_UNKNOWN_CMD = 0x01,
    ACK_BAD_VALUE   = 0x02
};

#define FLAG_RELAY_ON     0x01u
#define FLAG_SENSOR_FAULT 0x02u

/* Пакування обов'язкове: без нього GCC вирівняє seq за адресою, кратною 4,
   і структура розпухне з 16 байтів до 20 — на дроті це вже інший протокол. */
#pragma pack(push, 1)

typedef struct {
    uint8_t  magic;
    uint8_t  type;
    uint16_t node_id;
    uint32_t seq;
} frame_head_t;

typedef struct {
    frame_head_t head;
    int16_t      temp_c100;   /* сотні градуса: 2235 == 22.35 °C */
    uint16_t     battery_mv;
    uint8_t      flags;
    uint8_t      reserved;
    uint16_t     crc;
} telemetry_frame_t;

typedef struct {
    frame_head_t head;
    uint8_t      cmd_id;
    uint8_t      value;
    uint8_t      reserved[4];
    uint16_t     crc;
} command_frame_t;

typedef struct {
    frame_head_t head;
    uint8_t      cmd_id;
    uint8_t      status;
    uint8_t      flags;       /* стан вузла ПІСЛЯ застосування команди */
    uint8_t      reserved[3];
    uint16_t     crc;
} ack_frame_t;

#pragma pack(pop)

_Static_assert(sizeof(telemetry_frame_t) == FRAME_SIZE, "телеметрія не 16 байтів");
_Static_assert(sizeof(command_frame_t) == FRAME_SIZE, "команда не 16 байтів");
_Static_assert(sizeof(ack_frame_t) == FRAME_SIZE, "квитанція не 16 байтів");

uint16_t crc16_ccitt(const uint8_t *data, size_t len);

void frame_build_telemetry(uint8_t out[FRAME_SIZE], uint16_t node_id, uint32_t seq,
                           int16_t temp_c100, uint16_t battery_mv, uint8_t flags);

void frame_build_ack(uint8_t out[FRAME_SIZE], uint16_t node_id, uint32_t seq,
                     uint8_t cmd_id, uint8_t status, uint8_t flags);

/* Магія на місці й CRC зійшлася — саме за цим кадрувальник відрізняє
   справжній кадр від випадкового 0xAA всередині сміття. */
bool frame_valid(const uint8_t buf[FRAME_SIZE]);

uint8_t  frame_type_of(const uint8_t buf[FRAME_SIZE]);
uint16_t frame_node_of(const uint8_t buf[FRAME_SIZE]);

/* Розбирає валідований кадр команди. false — це не команда. */
bool frame_read_command(const uint8_t buf[FRAME_SIZE], command_frame_t *out);

#endif /* FRAME_H */
