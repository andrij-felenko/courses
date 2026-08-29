/* isa.h — система команд синтезованого 8-бітного ядра.
 *
 * Опкоди тут потрібні двом сторонам одразу: дешифратору інструкцій у cpu.c
 * і «асемблеру» в main.c, який руками складає бінарну прошивку. Тому вони
 * живуть окремим модулем, а не всередині ядра.
 */
#ifndef ISA_H
#define ISA_H

#include <stdbool.h>
#include <stdint.h>

enum {
    OP_NOP           = 0x00,
    OP_LOAD_IMM_ACC  = 0x01,
    OP_LOAD_IMM_R0   = 0x02,
    OP_LOAD_MEM_ACC  = 0x10,
    OP_STORE_MEM_ACC = 0x20,
    OP_ADD_ACC_R0    = 0x30,
    OP_SUB_ACC_R0    = 0x31,
    OP_AND_ACC_R0    = 0x32,
    OP_XOR_ACC_R0    = 0x33,
    OP_JMP           = 0x40,
    OP_JZ            = 0x41,
    OP_HALT          = 0xFF
};

/* Мнемоніка опкода. Для чужого байта повертає "???": ядро однаково впаде
   в пастку невідомої інструкції, але трасування мусить лишитися читабельним. */
const char *isa_mnemonic(uint8_t opcode);

/* Скільки байтів операнда лежить у пам'яті одразу за опкодом: 0, 1 або 2.
   Саме це число визначає, на скільки виросте PC за одну інструкцію
   (плюс сам байт опкода). Для чужого байта — 0. */
unsigned isa_operand_bytes(uint8_t opcode);

/* Чи належить байт нашій ISA. */
bool isa_is_valid(uint8_t opcode);

#endif /* ISA_H */
