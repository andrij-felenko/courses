/*
 * Бінарна схема правил: 16-байтний дескриптор, коди операцій,
 * карта регістрів стану, коди помилок валідації.
 *
 * Цей заголовок — спільний контракт прошивки й хаба: обидві сторони
 * складають той самий масив байтів. Порядок байтів — Little-Endian.
 */
#ifndef RULE_SCHEMA_H
#define RULE_SCHEMA_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define MAX_RULES_COUNT      32u
#define RULE_DESCRIPTOR_SIZE 16u

/* ── карта регістрів стану (StateRegisterMap) ───────────────────────── */
#define REG_SENSOR_FIRST     0x00u   /* давачі: для правил і хаба — тільки читання */
#define REG_SENSOR_LAST      0x0Fu
#define REG_ACTUATOR_FIRST   0x10u   /* реле, ШІМ, клапани */
#define REG_ACTUATOR_LAST    0x1Fu
#define REG_SETPOINT_FIRST   0x20u   /* цільові уставки й ліміти */
#define REG_SETPOINT_LAST    0x2Fu
#define REG_TIMER_FIRST      0x30u   /* програмні таймери: залишок у мс */
#define REG_TIMER_LAST       0x37u
#define REG_STATUS_FIRST     0x38u
#define REG_STATUS_LAST      0x3Fu
#define TOTAL_REGISTERS_NUM  0x40u

#define TIMER_COUNT          (REG_TIMER_LAST - REG_TIMER_FIRST + 1u)
/* Останнє гніздо таймерів закріплене за орендою керування від хаба:
   його заводить серцебиття, а не правила (валідація це стереже). */
#define TIMER_HUB_LEASE      (TIMER_COUNT - 1u)
#define REG_HUB_LEASE        (REG_TIMER_FIRST + TIMER_HUB_LEASE)

#define REG_STATUS_WORD      0x38u   /* режим рушія */
#define REG_ERROR_WORD       0x39u   /* бітова маска відкинутих дій */

#define STATUS_BIT_FALLBACK  (1u << 0)
#define STATUS_BIT_EMERGENCY (1u << 1)
#define STATUS_BIT_LATCHED   (1u << 2)

#define ERROR_BIT_RO_WRITE       (1u << 0)  /* спроба запису в давач */
#define ERROR_BIT_BAD_TIMER      (1u << 1)  /* таймер поза смугою 0x30..0x37 */
#define ERROR_BIT_REMOTE_BLOCKED (1u << 2)  /* дистанційну уставку відкинуто */

/* ── фіксована точка Q16.16 ─────────────────────────────────────────── */
#define Q16(x) ((int32_t)((x) * 65536.0))

static inline float q16_to_float(int32_t v) { return (float)v / 65536.0f; }

/* ── бітові прапорці правила ────────────────────────────────────────── */
typedef enum {
    RULE_FLAG_ENABLED         = (1u << 0),
    RULE_FLAG_SAFETY_CRITICAL = (1u << 1),
    RULE_FLAG_LATCHING        = (1u << 2),
    RULE_FLAG_INVERT_ACTION   = (1u << 3),
    RULE_FLAG_FALLBACK_ACTIVE = (1u << 4)
} rule_flags_t;

#define RULE_FLAGS_KNOWN_MASK 0x001Fu

typedef enum {
    OP_ALWAYS        = 0x01,
    OP_LESS_THAN     = 0x02,
    OP_GREATER_THAN  = 0x03,
    OP_EQUAL         = 0x04,
    OP_NOT_EQUAL     = 0x05,
    OP_BIT_SET       = 0x06,
    OP_BIT_CLEAR     = 0x07,
    OP_TIMER_EXPIRED = 0x08
} condition_opcode_t;

typedef enum {
    ACT_OUTPUT_SET     = 0x10,
    ACT_SET_SETPOINT   = 0x11,
    ACT_ARM_TIMER      = 0x12,
    ACT_DISARM_TIMER   = 0x13,
    ACT_EMERGENCY_STOP = 0x14,
    ACT_INHIBIT_REMOTE = 0x15
} action_opcode_t;

/* Коди помилок; вони ж їдуть у полі даних кадру NACK. */
typedef enum {
    ERR_NONE             = 0x00,
    ERR_BAD_SOF          = 0x10,
    ERR_TRUNCATED_FRAME  = 0x11,
    ERR_UNKNOWN_TYPE     = 0x12,
    ERR_LENGTH_ALIGN     = 0x13,
    ERR_CRC_MISMATCH     = 0x14,
    ERR_BUFFER_OVERFLOW  = 0x15,
    ERR_BAD_OPCODE       = 0x20,
    ERR_REG_OUT_OF_RANGE = 0x21,
    ERR_BAD_RESERVED     = 0x22,
    ERR_BAD_FLAGS        = 0x23,
    ERR_BAD_RULE_ID      = 0x24,
    ERR_DUPLICATE_ID     = 0x25,
    ERR_SAFETY_VIOLATION = 0x26,
    ERR_REG_READ_ONLY    = 0x30,
    ERR_REMOTE_INHIBITED = 0x31
} rule_error_t;

/* 16 байтів, кратні 4 — структуру можна накладати просто на буфер прийому. */
typedef struct __attribute__((packed)) {
    uint16_t rule_id;        /* 0 — маркер порожнього гнізда */
    uint16_t flags;
    uint8_t  cond_op;
    uint8_t  input_reg;
    uint16_t reserved;       /* при передачі — нулі */
    int32_t  threshold;      /* Q16.16 для фізичних величин */
    uint8_t  action_op;
    uint8_t  output_target;
    int16_t  action_param;
} rule_descriptor_t;

_Static_assert(sizeof(rule_descriptor_t) == RULE_DESCRIPTOR_SIZE, "дескриптор мусить бути рівно 16 Б");
_Static_assert(offsetof(rule_descriptor_t, flags)         == 2,  "зсув flags");
_Static_assert(offsetof(rule_descriptor_t, cond_op)       == 4,  "зсув cond_op");
_Static_assert(offsetof(rule_descriptor_t, input_reg)     == 5,  "зсув input_reg");
_Static_assert(offsetof(rule_descriptor_t, reserved)      == 6,  "зсув reserved");
_Static_assert(offsetof(rule_descriptor_t, threshold)     == 8,  "зсув threshold");
_Static_assert(offsetof(rule_descriptor_t, action_op)     == 12, "зсув action_op");
_Static_assert(offsetof(rule_descriptor_t, output_target) == 13, "зсув output_target");
_Static_assert(offsetof(rule_descriptor_t, action_param)  == 14, "зсув action_param");

static inline bool reg_is_sensor(uint8_t r)   { return r <= REG_SENSOR_LAST; }
static inline bool reg_is_actuator(uint8_t r) { return r >= REG_ACTUATOR_FIRST && r <= REG_ACTUATOR_LAST; }
static inline bool reg_is_setpoint(uint8_t r) { return r >= REG_SETPOINT_FIRST && r <= REG_SETPOINT_LAST; }
static inline bool reg_is_timer(uint8_t r)    { return r >= REG_TIMER_FIRST && r <= REG_TIMER_LAST; }
static inline bool reg_is_valid(uint8_t r)    { return r < TOTAL_REGISTERS_NUM; }

#endif /* RULE_SCHEMA_H */
