#include <stdint.h>

// Коди операцій АЛП
enum { OP_ADD = 0, OP_SUB = 1, OP_AND = 2, OP_OR = 3, OP_XOR = 4 };

// Прапорці стану (бітова маска)
enum { FLAG_Z = 1, FLAG_C = 2, FLAG_N = 4, FLAG_V = 8 };

#define ALU_BITS 8                      // ширина слова

// одна скибка: розряд a,b + перенос cin, код op → біт y, перенос cout
static uint8_t alu_slice(uint8_t a, uint8_t b, uint8_t cin,
                         uint8_t op, uint8_t *cout) {
    uint8_t sum  = a ^ b ^ cin;                       // біт суми = непарність трьох
    uint8_t carry= (a & b) | (cin & (a ^ b));         // перенос = «більшість»
    *cout = carry;
    switch (op) {                                     // мультиплексор за кодом
        case OP_AND: return a & b;
        case OP_OR:  return a | b;
        case OP_XOR: return a ^ b;
        default:     return sum;                      // ADD і SUB обидва йдуть сумою
    }
}

// n-бітний АЛП: рахує result і виставляє прапорці у *flags
uint32_t alu(uint32_t a, uint32_t b, uint8_t op, uint8_t *flags) {
    uint8_t is_arith = (op == OP_ADD || op == OP_SUB);
    uint8_t sub      = (op == OP_SUB);
    uint8_t cin      = sub;                           // SUB: початковий перенос = 1
    uint32_t result  = 0;
    uint8_t  cout    = 0, cprev = 0;

    for (int i = 0; i < ALU_BITS; i++) {
        uint8_t ai = (a >> i) & 1;
        uint8_t bi = (b >> i) & 1;
        bi ^= sub;                                    // SUB інвертує b (доповняльний код)
        cprev = cout;                                 // запам'ятати перенос ДО старшого біта
        uint8_t yi = alu_slice(ai, bi, cin, op, &cout);
        result |= (uint32_t)yi << i;
        cin = cout;                                   // перенос біжить у наступний розряд
    }

    // прапорці
    uint8_t f = 0;
    if ((result & ((1u << ALU_BITS) - 1)) == 0) f |= FLAG_Z;   // нуль
    if ((result >> (ALU_BITS - 1)) & 1)         f |= FLAG_N;   // знак
    if (is_arith) {
        if (cout)            f |= FLAG_C;                       // перенос за межі слова
        if (cout != cprev)   f |= FLAG_V;                       // знакове переповнення
    }
    *flags = f;
    return result & ((1u << ALU_BITS) - 1);
}
