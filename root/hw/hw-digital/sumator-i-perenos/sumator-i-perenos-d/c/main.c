#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Структура для повернення результату та метрики логічної затримки
typedef struct {
    uint64_t sum;
    uint8_t  carry_out;
    uint32_t gate_levels; // Кількість ярусів вентилів на критичному шляху
} AdderResult;

// Емуляція 64-розрядного ланцюгового суматора (Ripple Carry Adder)
AdderResult ripple_carry_adder_64(uint64_t a, uint64_t b, uint8_t cin) {
    AdderResult res;
    res.sum = 0;
    uint8_t c = cin & 1;
    uint32_t carry_chain_delay = 0;

    for (int i = 0; i < 64; i++) {
        uint8_t ai = (uint8_t)((a >> i) & 1);
        uint8_t bi = (uint8_t)((b >> i) & 1);

        // Повний суматор розряду:
        // S_i = ai ^ bi ^ c
        // Cout = (ai & bi) | (c & (ai ^ bi))
        uint8_t prop = (uint8_t)(ai ^ bi);
        uint8_t gen  = (uint8_t)(ai & bi);
        uint8_t si   = (uint8_t)(prop ^ c);
        c = (uint8_t)(gen | (c & prop));

        res.sum |= ((uint64_t)si << i);
        carry_chain_delay += 2; // Кожен каскад переносу додає 2 вентильні затримки (AND-OR / AOI)
    }

    res.carry_out = c;
    // Повний критичний шлях: 1 ярус підготовки (XOR) + 64 * 2 (переноси) + 1 ярус фінальної суми
    res.gate_levels = 1 + carry_chain_delay + 1;
    return res;
}

// Емуляція 64-розрядного суматора Коггі-Стоуна (Kogge-Stone Prefix Adder)
AdderResult kogge_stone_adder_64(uint64_t a, uint64_t b, uint8_t cin) {
    AdderResult res;
    res.sum = 0;

    uint8_t g[64];
    uint8_t p[64];

    // Рівень 0: Попередня генерація бітових сигналів g_i та p_i (1 вентильний ярус)
    for (int i = 0; i < 64; i++) {
        uint8_t ai = (uint8_t)((a >> i) & 1);
        uint8_t bi = (uint8_t)((b >> i) & 1);
        g[i] = (uint8_t)(ai & bi);
        p[i] = (uint8_t)(ai ^ bi);
    }

    // Врахування вхідного переносу cin у нульовий розряд
    g[0] = (uint8_t)(g[0] | (p[0] & (cin & 1)));

    uint8_t cur_g[64];
    uint8_t cur_p[64];
    for (int i = 0; i < 64; i++) {
        cur_g[i] = g[i];
        cur_p[i] = p[i];
    }

    uint32_t prefix_stages = 0;
    // Префіксне дерево: кроки зміщення 1, 2, 4, 8, 16, 32 (log2(64) = 6 ярусів)
    for (int stride = 1; stride < 64; stride <<= 1) {
        uint8_t next_g[64];
        uint8_t next_p[64];

        for (int i = 0; i < 64; i++) {
            if (i >= stride) {
                // Оператор "крапка" (G_L, P_L) o (G_R, P_R) = (G_L | (P_L & G_R), P_L & P_R)
                next_g[i] = (uint8_t)(cur_g[i] | (cur_p[i] & cur_g[i - stride]));
                next_p[i] = (uint8_t)(cur_p[i] & cur_p[i - stride]);
            } else {
                next_g[i] = cur_g[i];
                next_p[i] = cur_p[i];
            }
        }

        for (int i = 0; i < 64; i++) {
            cur_g[i] = next_g[i];
            cur_p[i] = next_p[i];
        }
        prefix_stages++;
    }

    // Фінальне формування бітів суми S_i = p_i ^ C_{i-1}
    for (int i = 0; i < 64; i++) {
        uint8_t c_in_bit = (i == 0) ? (cin & 1) : cur_g[i - 1];
        uint8_t si = (uint8_t)(p[i] ^ c_in_bit);
        res.sum |= ((uint64_t)si << i);
    }

    res.carry_out = cur_g[63];
    // Затримка: 1 (g/p) + 6 * 2 (кожен префіксний вузол AND-OR = 2 затримки) + 1 (фінальний XOR суми)
    res.gate_levels = 1 + (prefix_stages * 2) + 1;
    return res;
}

int main(void) {
    uint64_t a = 0x7FFFFFFFFFFFFFFF;
    uint64_t b = 0x0000000000000001;
    uint8_t cin = 0;

    AdderResult rca = ripple_carry_adder_64(a, b, cin);
    AdderResult ksa = kogge_stone_adder_64(a, b, cin);

    printf("64-Bit Addition Comparison (A = 0x%016llX, B = 0x%016llX)\n",
           (unsigned long long)a, (unsigned long long)b);
    printf("Hardware Result:        0x%016llX\n", (unsigned long long)(a + b + cin));
    printf("RCA Sum:                0x%016llX (Carry: %u, Gate Delay Depth: %u levels)\n",
           (unsigned long long)rca.sum, rca.carry_out, rca.gate_levels);
    printf("Kogge-Stone Sum:        0x%016llX (Carry: %u, Gate Delay Depth: %u levels)\n",
           (unsigned long long)ksa.sum, ksa.carry_out, ksa.gate_levels);

    if (rca.sum == (a + b + cin) && ksa.sum == (a + b + cin)) {
        printf("Verification: SUCCESS. Speedup factor in gate depth: %.2fx\n",
               (double)rca.gate_levels / (double)ksa.gate_levels);
    }
    return 0;
}
