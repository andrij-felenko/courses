#include "isa.h"

#include <stddef.h>

typedef struct {
    uint8_t     opcode;
    const char *mnemonic;
    unsigned    operand_bytes;
} IsaEntry;

/* Уся система команд одним місцем. У кремнії цій таблиці відповідає
   мікрокодове ПЗП або матриця вентилів дешифратора інструкцій. */
static const IsaEntry k_table[] = {
    { OP_NOP,           "NOP",           0 },
    { OP_LOAD_IMM_ACC,  "LOAD_IMM_ACC",  1 },
    { OP_LOAD_IMM_R0,   "LOAD_IMM_R0",   1 },
    { OP_LOAD_MEM_ACC,  "LOAD_MEM_ACC",  2 },
    { OP_STORE_MEM_ACC, "STORE_MEM_ACC", 2 },
    { OP_ADD_ACC_R0,    "ADD_ACC_R0",    0 },
    { OP_SUB_ACC_R0,    "SUB_ACC_R0",    0 },
    { OP_AND_ACC_R0,    "AND_ACC_R0",    0 },
    { OP_XOR_ACC_R0,    "XOR_ACC_R0",    0 },
    { OP_JMP,           "JMP",           2 },
    { OP_JZ,            "JZ",            2 },
    { OP_HALT,          "HALT",          0 }
};

static const size_t k_count = sizeof k_table / sizeof k_table[0];

static const IsaEntry *lookup(uint8_t opcode)
{
    for (size_t i = 0; i < k_count; ++i) {
        if (k_table[i].opcode == opcode) {
            return &k_table[i];
        }
    }
    return NULL;
}

const char *isa_mnemonic(uint8_t opcode)
{
    const IsaEntry *entry = lookup(opcode);
    return entry ? entry->mnemonic : "???";
}

unsigned isa_operand_bytes(uint8_t opcode)
{
    const IsaEntry *entry = lookup(opcode);
    return entry ? entry->operand_bytes : 0u;
}

bool isa_is_valid(uint8_t opcode)
{
    return lookup(opcode) != NULL;
}
