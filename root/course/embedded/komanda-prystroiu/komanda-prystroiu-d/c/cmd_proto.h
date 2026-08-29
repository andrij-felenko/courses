#ifndef CMD_PROTO_H
#define CMD_PROTO_H

/* Дротовий формат команди та квитанції.
 *
 * Кадр команди (усі багатобайтові поля — little-endian):
 *   зсув  розмір  поле
 *     0     4     magic  = "CMD1"
 *     4     1     version
 *     5     1     type          (cmd_type_t)
 *     6     4     seq           монотонний лічильник повідомлень (захист від повтору)
 *    10     8     token         токен ідемпотентності
 *    18     4     ttl_ms        залишок строку життя на момент передавання
 *    22     1     payload_len
 *    23    ..     payload
 *   +len    4     crc32         по всіх попередніх байтах
 *
 * Кадр квитанції (27 байтів): magic "ACK1", version, phase (1|2), state,
 * token, result (код помилки), detail (фінальний параметр), crc32.
 *
 * Розбір навмисно побайтовий, а не приведенням буфера до packed-структури:
 * на Cortex-M невирівняний доступ до uint64_t у прийомному буфері — це або
 * HardFault, або мовчазне псування даних, а порядок байтів у структурі
 * залежить від процесора, а не від протоколу. */

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define WIRE_VERSION     1u
#define WIRE_MAGIC_CMD   0x434D4431u   /* "CMD1" */
#define WIRE_MAGIC_ACK   0x41434B31u   /* "ACK1" */

#define CMD_HDR_LEN      23u
#define CMD_MAX_PAYLOAD  16u
#define CMD_MAX_FRAME    (CMD_HDR_LEN + CMD_MAX_PAYLOAD + 4u)
#define ACK_FRAME_LEN    27u

/* Типи команд. Абсолютні (SET_RELAY, GOTO_POS, CALIBRATE) природно
 * ідемпотентні; DISPENSE_ML — відносна дія, і саме заради неї існує токен. */
typedef enum {
    CMD_NOOP        = 0,
    CMD_SET_RELAY   = 1,   /* payload: u8 канал, u8 стан */
    CMD_GOTO_POS    = 2,   /* payload: i32 абсолютна позиція в кроках */
    CMD_DISPENSE_ML = 3,   /* payload: u16 мілілітри (НЕ ідемпотентна) */
    CMD_CALIBRATE   = 4    /* payload: немає */
} cmd_type_t;

/* Стани життєвого циклу команди всередині пристрою. */
typedef enum {
    ST_FREE      = 0,
    ST_ACCEPTED  = 1,   /* прийнято, стоїть у черзі диспетчера */
    ST_EXECUTING = 2,   /* привід у русі */
    ST_SUCCEEDED = 3,
    ST_FAILED    = 4,
    ST_EXPIRED   = 5
} cmd_state_t;

typedef enum {
    E_OK           = 0,
    E_SHORT_FRAME  = -1,
    E_BAD_MAGIC    = -2,
    E_BAD_VERSION  = -3,
    E_BAD_CRC      = -4,
    E_BAD_LENGTH   = -5,
    E_REPLAY       = -6,
    E_EXPIRED      = -7,
    E_SUPERSEDED   = -8,
    E_NO_SLOT      = -9,
    E_QUEUE_FULL   = -10,
    E_UNKNOWN_TYPE = -11,
    E_BAD_PAYLOAD  = -12,
    E_SUPPLY_SAG   = -13,
    E_STALL        = -14,
    E_POWER_RESET  = -15
} cmd_err_t;

typedef struct {
    uint64_t token;
    uint32_t seq;
    uint32_t ttl_ms;
    uint8_t  type;
    uint8_t  payload_len;
    uint8_t  payload[CMD_MAX_PAYLOAD];
} cmd_frame_t;

typedef struct {
    uint64_t token;
    uint8_t  phase;    /* 1 — прийнято, 2 — термінальний стан */
    uint8_t  state;
    int32_t  result;
    int32_t  detail;
} ack_t;

uint32_t wire_crc32(const uint8_t *data, size_t len);

/* Розбір і збирання кадрів. Повертають код помилки / довжину кадру (0 = не вліз). */
cmd_err_t wire_parse_command(const uint8_t *buf, size_t len, cmd_frame_t *out);
size_t    wire_build_command(const cmd_frame_t *f, uint8_t *buf, size_t cap);
size_t    wire_build_ack(const ack_t *a, uint8_t *buf, size_t cap);
bool      wire_parse_ack(const uint8_t *buf, size_t len, ack_t *out);

/* Побайтові читання/записи little-endian — потрібні й корисному навантаженню. */
void     wire_put_u16(uint8_t *p, uint16_t v);
void     wire_put_i32(uint8_t *p, int32_t v);
uint16_t wire_get_u16(const uint8_t *p);
int32_t  wire_get_i32(const uint8_t *p);

const char *cmd_type_name(uint8_t type);
const char *cmd_state_name(uint8_t state);
const char *cmd_err_name(int32_t err);

#endif /* CMD_PROTO_H */
