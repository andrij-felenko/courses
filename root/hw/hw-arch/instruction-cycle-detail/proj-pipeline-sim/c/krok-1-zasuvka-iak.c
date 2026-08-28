#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

enum { OP_NOP, OP_LOAD, OP_ADD, OP_STORE, OP_HALT };

// Одна засувка (pipeline register): усе, що команда несе між стадіями.
typedef struct {
    bool     valid;    // true — справжня команда; false — порожній слот (бульбашка)
    uint8_t  op;       // яка операція (OP_*)
    uint8_t  rd;       // регістр призначення
    uint8_t  rs1, rs2; // регістри-джерела
    uint16_t addr;     // адреса для LOAD/STORE
    int32_t  a, b;     // операнди, прочитані з регістрів (для АЛП / значення STORE)
    int32_t  alu;      // результат АЛП
    int32_t  memdata;  // число, привезене з пам'яті (для LOAD)
} Latch;
