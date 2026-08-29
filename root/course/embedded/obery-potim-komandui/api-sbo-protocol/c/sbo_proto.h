/* Профіль Select-Before-Operate: константи розділів 1–6 і структура кадру.
   Заголовок описує ДРІТ: розкладку байтів, коди повідомлень, стани, команди
   й коди відмов. Логіки тут немає — лише те, про що домовилися сторони. */
#ifndef SBO_PROTO_H
#define SBO_PROTO_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* --- Розділ 1: розкладка кадру -------------------------------------- */

#define SBO_MAGIC        0x5Bu   /* сигнатура початку кадру, ASCII '[' */
#define SBO_HEADER_LEN   16u     /* фіксована частина: magic … timeout_ms */
#define SBO_CRC_LEN      2u
#define SBO_MAX_PAYLOAD  128u
#define SBO_MAX_FRAME    (SBO_HEADER_LEN + SBO_MAX_PAYLOAD + SBO_CRC_LEN)

/* Адреси. 0xFF — широкомовна, апарати мають ID 1–240. */
#define SBO_ADDR_BROADCAST 0xFFu
#define SBO_ADDR_GCS       0xFEu
#define SBO_ADDR_RELAY     0xFDu

/* Підсистеми всередині апарата (target_comp). */
#define SBO_COMP_FC   0x01u
#define SBO_COMP_ESC  0x02u
#define SBO_COMP_NAV  0x03u

/* --- Розділ 2: типи повідомлень ------------------------------------- */

enum sbo_msg_type {
    SBO_MSG_SELECT_REQ   = 0x10,
    SBO_MSG_SELECT_ACK   = 0x11,
    SBO_MSG_SELECT_NACK  = 0x12,
    SBO_MSG_OPERATE_REQ  = 0x20,
    SBO_MSG_OPERATE_ACK  = 0x21,
    SBO_MSG_OPERATE_NACK = 0x22,
    SBO_MSG_CANCEL_REQ   = 0x30,
    SBO_MSG_CANCEL_ACK   = 0x31,
    SBO_MSG_STATUS_PING  = 0x40,
    SBO_MSG_STATUS_PONG  = 0x41
};

/* --- Розділ 3: стани селектора -------------------------------------- */

enum sbo_state {
    SBO_STATE_IDLE      = 0x00,
    SBO_STATE_ARMED     = 0x01,
    SBO_STATE_EXECUTING = 0x02
};

/* --- Розділ 4: реєстр команд ---------------------------------------- */

enum sbo_cmd {
    CMD_PING                  = 0x0001,
    CMD_REQUEST_TELEMETRY     = 0x0002,
    CMD_EMERGENCY_MOTOR_CUT   = 0x0101,
    CMD_FORCE_DISARM          = 0x0102,
    CMD_FLIGHT_MODE_OVERRIDE  = 0x0103,
    CMD_REBOOT_AUTOPILOT      = 0x0104,
    CMD_FACTORY_RESET_PARAMS  = 0x0105,
    CMD_PAYLOAD_DROP_ACTUATE  = 0x0106
};

/* Межа класу безпеки: усе від 0x0100 вимагає проходження селекції. */
#define SBO_CRITICAL_BASE 0x0100u

/* --- Розділ 5: коди відмов ------------------------------------------ */

enum sbo_error {
    ERR_SBO_BUSY                 = 0x01,
    ERR_SBO_INVALID_TOKEN        = 0x02,
    ERR_SBO_TIMEOUT_EXPIRED      = 0x03,
    ERR_SBO_NOT_ARMED            = 0x04,
    ERR_SBO_CMD_MISMATCH         = 0x05,
    ERR_SBO_BROADCAST_FORBIDDEN  = 0x06,
    ERR_SBO_HARDWARE_FAULT       = 0x07
};

/* --- Розділ 6: часові параметри -------------------------------------- */

#define SBO_T_ARM_MIN_MS      1000u
#define SBO_T_ARM_DEFAULT_MS  5000u
#define SBO_T_ARM_MAX_MS     15000u
#define SBO_T_ACK_WAIT_MS      400u
#define SBO_T_COOLDOWN_MS     1000u
#define SBO_N_RETRY              2u

/* --- Розділ 8: прапорці SBO в пакеті стану --------------------------- */

#define SBO_FLAG_ARMED        0x01u
#define SBO_FLAG_LAST_REJECT  0x02u

/* --- Розібраний кадр -------------------------------------------------- */

struct sbo_frame {
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
    uint8_t  payload[SBO_MAX_PAYLOAD];
};

enum sbo_decode_result {
    SBO_DECODE_OK = 0,
    SBO_DECODE_SHORT,      /* байтів менше, ніж обіцяє payload_len */
    SBO_DECODE_BAD_MAGIC,
    SBO_DECODE_BAD_LEN,    /* payload_len поза 0..128 або зайвий хвіст */
    SBO_DECODE_BAD_CRC
};

/* CRC-16-CCITT: поліном 0x1021, init 0xFFFF, старшим бітом уперед. */
uint16_t sbo_crc16_ccitt(const uint8_t *data, size_t len);

/* Збирає кадр у буфер. Повертає довжину або 0, якщо буфер замалий. */
size_t sbo_encode(const struct sbo_frame *f, uint8_t *out, size_t cap);

/* Розбирає кадр: сигнатура, довжина, контрольна сума — усе перевірене. */
enum sbo_decode_result sbo_decode(const uint8_t *buf, size_t len, struct sbo_frame *out);

bool     sbo_cmd_is_critical(uint16_t cmd_code);
uint16_t sbo_clamp_window(uint16_t timeout_ms);

const char *sbo_msg_name(uint8_t msg_type);
const char *sbo_state_name(uint8_t state);
const char *sbo_error_name(uint8_t code);

#endif /* SBO_PROTO_H */
