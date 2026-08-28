#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    ALU_OP_ADD = 0,
    ALU_OP_SUB = 1,
    ALU_OP_AND = 2,
    ALU_OP_OR  = 3,
    ALU_OP_XOR = 4,
    ALU_OP_NOT = 5,
    ALU_OP_LSL = 6,
    ALU_OP_LSR = 7,
    ALU_OP_ASR = 8
} alu_opcode_t;

typedef struct {
    bool C; /* Carry / Borrow */
    bool Z; /* Zero */
    bool N; /* Negative / Sign */
    bool V; /* Overflow */
} alu_flags_t;

typedef struct {
    alu_flags_t flags;
} alu_t;

void alu_init(alu_t *alu) {
    alu->flags.C = false;
    alu->flags.Z = false;
    alu->flags.N = false;
    alu->flags.V = false;
}

/* Однобітний повний суматор на вентилях */
static inline void full_adder_bit(bool a, bool b, bool cin, bool *sum, bool *cout) {
    *sum = a ^ b ^ cin;
    *cout = (a & b) | (cin & (a ^ b));
}

uint8_t alu_execute(alu_t *alu, alu_opcode_t op, uint8_t a, uint8_t b) {
    uint8_t result = 0;
    alu->flags.C = false;
    alu->flags.V = false;

    if (op == ALU_OP_ADD || op == ALU_OP_SUB) {
        bool is_sub = (op == ALU_OP_SUB);
        bool carry = is_sub; /* Cin[0] = 1 при відніманні для доповняльного коду */
        bool last_cin = false;

        for (int i = 0; i < 8; ++i) {
            bool a_bit = (a >> i) & 1;
            bool b_bit = (b >> i) & 1;
            bool b_effective = b_bit ^ is_sub; /* Керований інвертор B */

            if (i == 7) {
                last_cin = carry; /* Зберігаємо вхідний перенос у старший 7-й біт */
            }

            bool s_bit, cout_bit;
            full_adder_bit(a_bit, b_effective, carry, &s_bit, &cout_bit);
            result |= (s_bit << i);
            carry = cout_bit;
        }

        /* Обчислення апаратних прапорців */
        alu->flags.C = carry;                     /* Беззнаковий перенос / вихід із 7-го біта */
        alu->flags.V = last_cin ^ carry;          /* V = Cin[7] XOR Cout[7] */
    } else {
        switch (op) {
            case ALU_OP_AND: result = a & b; break;
            case ALU_OP_OR:  result = a | b; break;
            case ALU_OP_XOR: result = a ^ b; break;
            case ALU_OP_NOT: result = ~a;    break;
            case ALU_OP_LSL:
                alu->flags.C = (a & 0x80) != 0;
                result = (uint8_t)(a << 1);
                break;
            case ALU_OP_LSR:
                alu->flags.C = (a & 0x01) != 0;
                result = (uint8_t)(a >> 1);
                break;
            case ALU_OP_ASR:
                alu->flags.C = (a & 0x01) != 0;
                result = (uint8_t)(((int8_t)a) >> 1);
                break;
            default: break;
        }
    }

    /* Прапорці Zero та Negative визначаються для всіх операцій */
    alu->flags.Z = (result == 0);
    alu->flags.N = (result & 0x80) != 0;

    return result;
}

void print_alu_state(const char *name, uint8_t a, uint8_t b, uint8_t res, const alu_flags_t *f) {
    printf("%-5s: A=0x%02X (%4d) | B=0x%02X (%4d) -> RES=0x%02X (%4d) | Flags: [Z=%d N=%d C=%d V=%d]\n",
           name, a, (int8_t)a, b, (int8_t)b, res, (int8_t)res, f->Z, f->N, f->C, f->V);
}

int main(void) {
    alu_t alu;
    alu_init(&alu);

    printf("=== Демонстрація роботи 8-бітного симулятора АЛУ (C) ===\n\n");

    /* Тест 1: Звичайне додавання без прапорців */
    uint8_t r1 = alu_execute(&alu, ALU_OP_ADD, 0x14, 0x1E); /* 20 + 30 = 50 */
    print_alu_state("ADD", 0x14, 0x1E, r1, &alu.flags);

    /* Тест 2: Беззнакове переповнення (Carry) */
    uint8_t r2 = alu_execute(&alu, ALU_OP_ADD, 0xFF, 0x01); /* 255 + 1 = 0, C=1, Z=1 */
    print_alu_state("ADD", 0xFF, 0x01, r2, &alu.flags);

    /* Тест 3: Знакове переповнення (Overflow) */
    uint8_t r3 = alu_execute(&alu, ALU_OP_ADD, 0x7F, 0x01); /* +127 + 1 = -128, V=1, N=1 */
    print_alu_state("ADD", 0x7F, 0x01, r3, &alu.flags);

    /* Тест 4: Віднімання з позикою */
    uint8_t r4 = alu_execute(&alu, ALU_OP_SUB, 0x05, 0x0A); /* 5 - 10 = -5 (0xFB) */
    print_alu_state("SUB", 0x05, 0x0A, r4, &alu.flags);

    /* Тест 5: Логічний зсув вліво */
    uint8_t r5 = alu_execute(&alu, ALU_OP_LSL, 0x85, 0x00); /* 10000101 << 1 = 00001010, C=1 */
    print_alu_state("LSL", 0x85, 0x00, r5, &alu.flags);

    return 0;
}
