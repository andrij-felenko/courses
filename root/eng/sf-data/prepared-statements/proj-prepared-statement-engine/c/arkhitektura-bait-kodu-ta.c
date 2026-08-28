#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_ROWS 1000
#define MAX_OPCODES 64
#define MAX_PARAMS 8

typedef enum {
    VAL_INT,
    VAL_STR
} ValType;

typedef struct {
    ValType type;
    union {
        int64_t i64;
        char str[64];
    } as;
} Value;

typedef struct {
    int64_t id;
    char name[32];
} UserRecord;

typedef enum {
    OP_SCAN_BEGIN,
    OP_CHECK_ID_EQ_PARAM,
    OP_CHECK_NAME_EQ_PARAM,
    OP_EMIT_ROW,
    OP_SCAN_NEXT,
    OP_HALT
} Opcode;

typedef struct {
    Opcode op;
    int param_idx; // індекс параметра у масиві зв'язування
} Instruction;

typedef struct {
    Instruction code[MAX_OPCODES];
    size_t code_len;
    size_t param_count;
    char template_sql[128];
} PreparedPlan;

// Кеш підготовлених планів
typedef struct {
    PreparedPlan plans[16];
    size_t count;
} PlanCache;

// Компіляція шаблону в байт-код
bool compile_plan(const char *sql_template, PreparedPlan *out_plan) {
    memset(out_plan, 0, sizeof(PreparedPlan));
    strncpy(out_plan->template_sql, sql_template, sizeof(out_plan->template_sql) - 1);

    // Спрощений синтаксичний аналізатор для демонстрації
    if (strstr(sql_template, "WHERE id = ?") != NULL) {
        out_plan->code[0] = (Instruction){OP_SCAN_BEGIN, 0};
        out_plan->code[1] = (Instruction){OP_CHECK_ID_EQ_PARAM, 0}; // параметр $0
        out_plan->code[2] = (Instruction){OP_EMIT_ROW, 0};
        out_plan->code[3] = (Instruction){OP_SCAN_NEXT, 0};
        out_plan->code[4] = (Instruction){OP_HALT, 0};
        out_plan->code_len = 5;
        out_plan->param_count = 1;
        return true;
    } else if (strstr(sql_template, "WHERE name = ?") != NULL) {
        out_plan->code[0] = (Instruction){OP_SCAN_BEGIN, 0};
        out_plan->code[1] = (Instruction){OP_CHECK_NAME_EQ_PARAM, 0}; // параметр $0
        out_plan->code[2] = (Instruction){OP_EMIT_ROW, 0};
        out_plan->code[3] = (Instruction){OP_SCAN_NEXT, 0};
        out_plan->code[4] = (Instruction){OP_HALT, 0};
        out_plan->code_len = 5;
        out_plan->param_count = 1;
        return true;
    }
    return false;
}

// Виконання байт-коду віртуальною машиною
size_t vm_execute(const PreparedPlan *plan, const Value *params, 
                  const UserRecord *table, size_t row_count, 
                  UserRecord *out_results) {
    size_t ip = 0; // Instruction Pointer
    size_t cursor = 0;
    size_t matched = 0;
    bool current_match = false;

    while (ip < plan->code_len) {
        Instruction inst = plan->code[ip];
        switch (inst.op) {
            case OP_SCAN_BEGIN:
                cursor = 0;
                current_match = false;
                ip++;
                break;

            case OP_CHECK_ID_EQ_PARAM:
                if (cursor < row_count && params[inst.param_idx].type == VAL_INT) {
                    current_match = (table[cursor].id == params[inst.param_idx].as.i64);
                } else {
                    current_match = false;
                }
                ip++;
                break;

            case OP_CHECK_NAME_EQ_PARAM:
                if (cursor < row_count && params[inst.param_idx].type == VAL_STR) {
                    current_match = (strcmp(table[cursor].name, 
                                            params[inst.param_idx].as.str) == 0);
                } else {
                    current_match = false;
                }
                ip++;
                break;

            case OP_EMIT_ROW:
                if (current_match && cursor < row_count) {
                    out_results[matched++] = table[cursor];
                }
                ip++;
                break;

            case OP_SCAN_NEXT:
                cursor++;
                if (cursor < row_count) {
                    ip = 1; // повернення до першої перевірки для наступного рядка
                } else {
                    ip++;
                }
                break;

            case OP_HALT:
                return matched;
        }
    }
    return matched;
}
