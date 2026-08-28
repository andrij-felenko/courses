#include <stdint.h>
#include <stdbool.h>

#define MAX_RULES 16
#define MAX_REGS  32

typedef enum {
    FLAG_ENABLED         = (1 << 0),
    FLAG_SAFETY_CRITICAL = (1 << 1),
    FLAG_LATCHED         = (1 << 2)
} rule_flag_t;

typedef enum {
    OP_NOP          = 0,
    OP_LESS_THAN    = 1,
    OP_GREATER_THAN = 2,
    OP_EQUAL        = 3
} rule_op_t;

typedef enum {
    ACT_NONE        = 0,
    ACT_SET_OUTPUT  = 1,
    ACT_CLEAR_OUT   = 2,
    ACT_EMERGENCY   = 3
} rule_act_t;

typedef struct {
    uint16_t   id;
    uint16_t   flags;
    rule_op_t  op;
    uint8_t    in_reg;
    int32_t    threshold;
    rule_act_t action;
    uint8_t    out_reg;
    int16_t    param;
} rule_entry_t;

typedef struct {
    int32_t      registers[MAX_REGS];
    rule_entry_t rules[MAX_RULES];
    uint8_t      rule_count;
    bool         emergency_latched;
} edge_engine_t;

void edge_engine_init(edge_engine_t *eng) {
    eng->rule_count = 0;
    eng->emergency_latched = false;
    for (int i = 0; i < MAX_REGS; ++i) {
        eng->registers[i] = 0;
    }
}

void edge_engine_step(edge_engine_t *eng) {
    for (uint8_t i = 0; i < eng->rule_count; ++i) {
        rule_entry_t *r = &eng->rules[i];
        if (!(r->flags & FLAG_ENABLED)) {
            continue;
        }

        int32_t val = eng->registers[r->in_reg];
        bool condition_met = false;

        switch (r->op) {
            case OP_LESS_THAN:    condition_met = (val < r->threshold); break;
            case OP_GREATER_THAN: condition_met = (val > r->threshold); break;
            case OP_EQUAL:        condition_met = (val == r->threshold); break;
            default: break;
        }

        if (condition_met) {
            switch (r->action) {
                case ACT_SET_OUTPUT:
                    eng->registers[r->out_reg] = r->param;
                    break;
                case ACT_CLEAR_OUT:
                    eng->registers[r->out_reg] = 0;
                    break;
                case ACT_EMERGENCY:
                    eng->emergency_latched = true;
                    eng->registers[r->out_reg] = 0; /* Негайне знеструмлення */
                    break;
                default: break;
            }
        }
    }
}
