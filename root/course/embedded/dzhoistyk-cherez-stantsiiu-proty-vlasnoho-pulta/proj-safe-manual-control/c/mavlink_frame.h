#ifndef MAVLINK_FRAME_H
#define MAVLINK_FRAME_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Кодек MAVLink рівно під ті повідомлення, які потрібні арбітру:
 * HEARTBEAT #0, MANUAL_CONTROL #69, COMMAND_LONG #76 і COMMAND_ACK #77 на відповідь.
 * Розбираються обидві версії кадру — v1 (0xFE) і v2 (0xFD), із підписом
 * і з обрізанням хвостових нулів, як його робить передавач v2. */

#define MAV_STX_V1        0xFEu
#define MAV_STX_V2        0xFDu
#define MAV_MAX_PAYLOAD   255
#define MAV_SIGNATURE_LEN 13

#define MAV_MSG_HEARTBEAT      0u
#define MAV_MSG_MANUAL_CONTROL 69u
#define MAV_MSG_COMMAND_LONG   76u
#define MAV_MSG_COMMAND_ACK    77u

#define MAV_CMD_COMPONENT_ARM_DISARM 400u

#define MAV_RESULT_ACCEPTED             0u
#define MAV_RESULT_TEMPORARILY_REJECTED 1u
#define MAV_RESULT_DENIED               2u
#define MAV_RESULT_UNSUPPORTED          3u
#define MAV_RESULT_FAILED               4u

#define MAV_COMP_ID_AUTOPILOT1     1u
#define MAV_COMP_ID_MISSIONPLANNER 190u
#define MAV_COMP_ID_ALL            0u

typedef struct {
    uint8_t  sysid;
    uint8_t  compid;
    uint8_t  seq;
    uint32_t msgid;
    uint8_t  len;                        /* стільки байтів реально прийшло */
    uint8_t  payload[MAV_MAX_PAYLOAD];   /* хвіст добитий нулями до канонічної довжини */
} mav_frame_t;

typedef struct {
    uint8_t  state;
    bool     is_v2;
    uint8_t  incompat, compat, seq, sysid, compid, len, idx, skip;
    uint32_t msgid;
    uint16_t crc, rx_crc;
    uint8_t  payload[MAV_MAX_PAYLOAD];

    uint32_t stat_ok;          /* кадрів прийнято */
    uint32_t stat_crc_err;     /* биті кадри — шум в ефірі або обрив */
    uint32_t stat_unknown;     /* повідомлення поза нашим діалектом */
    uint32_t stat_unsupported; /* нерозпізнані incompat-прапорці */
} mav_parser_t;

/* Розібрані повідомлення. */
typedef struct {
    uint32_t custom_mode;
    uint8_t  type, autopilot, base_mode, system_status, mavlink_version;
} mav_heartbeat_t;

typedef struct {
    int16_t  x, y, z, r;
    uint16_t buttons;
    uint8_t  target;
} mav_manual_control_t;

typedef struct {
    float    param[7];
    uint16_t command;
    uint8_t  target_system, target_component, confirmation;
} mav_command_long_t;

typedef struct {
    uint16_t command;
    uint8_t  result;
} mav_command_ack_t;

void mav_parser_init(mav_parser_t *p);

/* Повертає true рівно тоді, коли байт завершив цілий і CRC-коректний кадр. */
bool mav_parse_byte(mav_parser_t *p, uint8_t byte, mav_frame_t *out);

/* Пакування payload'ів (порядок полів — з визначення повідомлення). */
uint8_t mav_pack_heartbeat(uint8_t *p, const mav_heartbeat_t *m);
uint8_t mav_pack_manual_control(uint8_t *p, const mav_manual_control_t *m);
uint8_t mav_pack_command_long(uint8_t *p, const mav_command_long_t *m);
uint8_t mav_pack_command_ack(uint8_t *p, const mav_command_ack_t *m);

void mav_unpack_heartbeat(const mav_frame_t *f, mav_heartbeat_t *m);
void mav_unpack_manual_control(const mav_frame_t *f, mav_manual_control_t *m);
void mav_unpack_command_long(const mav_frame_t *f, mav_command_long_t *m);

/* Збирає кадр v2 (з обрізанням нулів) у буфер; повертає довжину, 0 — не влізло. */
size_t mav_encode(uint8_t *buf, size_t cap, uint8_t sysid, uint8_t compid,
                  uint8_t seq, uint32_t msgid, const uint8_t *payload, uint8_t len);

#endif /* MAVLINK_FRAME_H */
