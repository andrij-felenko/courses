/* sbo_protocol.h — Кадр протоколу Select-Before-Operate: типи, коди, кодування.
 * Жодної динамічної памʼяті: усі структури фіксованого розміру. */
#ifndef SBO_PROTOCOL_H
#define SBO_PROTOCOL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define SBO_MAGIC_BYTE          0x5Bu
#define SBO_BROADCAST_ID        0xFFu
#define SBO_GCS_DEFAULT_ID      0xFEu
#define SBO_DEFAULT_TIMEOUT_MS  5000u
#define SBO_MAX_TIMEOUT_MS      30000u   /* стеля вікна: далекий вузол не диктує нам годину */
#define SBO_MAX_PAYLOAD_LEN     64u

/* Розкладка кадру на дроті (усі багатобайтові поля — little-endian):
 *   0 magic · 1 payload_len · 2 seq · 3 msg_type · 4 source_id · 5 target_id
 *   6 target_comp · 7 sbo_state · 8..11 sbo_token · 12..13 cmd_code
 *   14..15 timeout_ms · 16.. payload · далі crc16 над усім попереднім        */
#define SBO_HEADER_LEN          16u
#define SBO_CRC_LEN             2u
#define SBO_MIN_FRAME_LEN       (SBO_HEADER_LEN + SBO_CRC_LEN)
#define SBO_MAX_FRAME_LEN       (SBO_HEADER_LEN + SBO_MAX_PAYLOAD_LEN + SBO_CRC_LEN)

typedef enum {
    SBO_STATE_IDLE      = 0,
    SBO_STATE_ARMED     = 1,
    SBO_STATE_EXECUTING = 2
} sbo_fsm_state_t;

typedef enum {
    SBO_MSG_SELECT_REQ   = 0x10,
    SBO_MSG_SELECT_ACK   = 0x11,
    SBO_MSG_SELECT_NACK  = 0x12,
    SBO_MSG_OPERATE_REQ  = 0x20,
    SBO_MSG_OPERATE_ACK  = 0x21,
    SBO_MSG_OPERATE_NACK = 0x22,
    SBO_MSG_CANCEL_REQ   = 0x30,
    SBO_MSG_CANCEL_ACK   = 0x31,
    SBO_MSG_CANCEL_NACK  = 0x32
} sbo_msg_type_t;

typedef enum {
    SBO_ERR_NONE = 0,
    SBO_ERR_BUSY,                 /* замок тримає інший оператор або триває дія */
    SBO_ERR_INVALID_TOKEN,
    SBO_ERR_TIMEOUT_EXPIRED,      /* вікно селекції спливло саме на цьому кадрі */
    SBO_ERR_NOT_ARMED,
    SBO_ERR_CMD_MISMATCH,
    SBO_ERR_SOURCE_MISMATCH,      /* токен підставили з чужої адреси */
    SBO_ERR_BROADCAST_FORBIDDEN,
    SBO_ERR_FOREIGN_TARGET,       /* кадр адресовано іншому вузлу — мовчимо */
    SBO_ERR_BAD_MAGIC,
    SBO_ERR_BAD_LENGTH,
    SBO_ERR_BAD_CRC,
    SBO_ERR_UNKNOWN_TYPE,
    SBO_ERR_INTERNAL_FAULT
} sbo_error_t;

/* Розібраний кадр. Тримається на стеку задачі або в .bss, ніколи не в купі. */
typedef struct {
    uint8_t  magic;
    uint8_t  payload_len;
    uint8_t  seq;
    uint8_t  msg_type;
    uint8_t  source_id;
    uint8_t  target_id;
    uint8_t  target_comp;
    uint8_t  sbo_state;
    uint32_t sbo_token;
    uint16_t cmd_code;
    uint16_t timeout_ms;
    uint8_t  payload[SBO_MAX_PAYLOAD_LEN];
} sbo_packet_t;

/* CRC-16/CCITT-FALSE (поліном 0x1021, початкове 0xFFFF), побітово: таблиця на
 * 512 байтів у Flash дорожча за десяток тактів на кадр. */
uint16_t sbo_crc16(const uint8_t *data, size_t len);

bool sbo_msg_type_is_known(uint8_t msg_type);

/* Серіалізація вручну, а не memcpy структури: пакування й порядок байтів мають
 * бути однакові на Cortex-M, RISC-V і на пульті під x86. */
sbo_error_t sbo_frame_encode(const sbo_packet_t *pkt, uint8_t *buf, size_t cap, size_t *out_len);

/* Валідатор входу: довжина, magic, узгодженість payload_len, CRC, відомий тип. */
sbo_error_t sbo_frame_decode(const uint8_t *buf, size_t len, sbo_packet_t *out);

const char *sbo_error_text(sbo_error_t err);

#endif /* SBO_PROTOCOL_H */
