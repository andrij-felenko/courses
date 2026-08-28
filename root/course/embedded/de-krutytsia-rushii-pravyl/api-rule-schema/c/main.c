#include <stdint.h>
#include <stdbool.h>

#define MAX_RULES_COUNT      32
#define TOTAL_REGISTERS_NUM  64

typedef enum {
    RULE_FLAG_ENABLED         = (1 << 0),
    RULE_FLAG_SAFETY_CRITICAL = (1 << 1),
    RULE_FLAG_LATCHING        = (1 << 2),
    RULE_FLAG_INVERT_ACTION   = (1 << 3),
    RULE_FLAG_FALLBACK_ACTIVE = (1 << 4)
} rule_flags_t;

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
    ACT_OUTPUT_SET      = 0x10,
    ACT_SET_SETPOINT    = 0x11,
    ACT_ARM_TIMER       = 0x12,
    ACT_DISARM_TIMER    = 0x13,
    ACT_EMERGENCY_STOP  = 0x14,
    ACT_INHIBIT_REMOTE  = 0x15
} action_opcode_t;

typedef struct __attribute__((packed)) {
    uint16_t rule_id;
    uint16_t flags;
    uint8_t  cond_op;
    uint8_t  input_reg;
    uint16_t reserved;
    int32_t  threshold;
    uint8_t  action_op;
    uint8_t  output_target;
    int16_t  action_param;
} rule_descriptor_t;

typedef struct {
    int32_t registers[TOTAL_REGISTERS_NUM];
    rule_descriptor_t rules[MAX_RULES_COUNT];
    uint8_t active_rule_count;
    bool fallback_active;
    uint32_t last_eval_timestamp_ms;
} rule_engine_context_t;
