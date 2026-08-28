#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef unsigned __int128 uint128_t;

typedef struct {
    uint128_t x;
    uint128_t y;
    bool found;
} PellSolution;

void print_u128(uint128_t val) {
    if (val == 0) {
        printf("0");
        return;
    }
    char buf[64];
    int idx = 0;
    while (val > 0) {
        buf[idx++] = '0' + (int)(val % 10);
        val /= 10;
    }
    for (int i = idx - 1; i >= 0; --i) {
        putchar(buf[i]);
    }
}

PellSolution pell_solve_fundamental(uint64_t d) {
    PellSolution res = {0, 0, false};
    uint64_t a0 = (uint64_t)sqrt((double)d);
    if (a0 * a0 == d) {
        return res; // D є повним квадратом, нетривіальних розв'язків нема
    }

    uint64_t m = 0;
    uint64_t d_denom = 1;
    uint64_t a = a0;

    uint128_t p_prev2 = 0, p_prev1 = 1, p_curr = a0;
    uint128_t q_prev2 = 1, q_prev1 = 0, q_curr = 1;

    while (1) {
        if (p_curr * p_curr - (uint128_t)d * q_curr * q_curr == 1) {
            res.x = p_curr;
            res.y = q_curr;
            res.found = true;
            return res;
        }

        m = d_denom * a - m;
        d_denom = (d - m * m) / d_denom;
        a = (a0 + m) / d_denom;

        p_prev2 = p_prev1;
        p_prev1 = p_curr;
        p_curr = (uint128_t)a * p_prev1 + p_prev2;

        q_prev2 = q_prev1;
        q_prev1 = q_curr;
        q_curr = (uint128_t)a * q_prev1 + q_prev2;
    }
}

PellSolution pell_next_solution(PellSolution fund, PellSolution prev, uint64_t d) {
    PellSolution next;
    next.x = fund.x * prev.x + (uint128_t)d * fund.y * prev.y;
    next.y = fund.y * prev.x + fund.x * prev.y;
    next.found = true;
    return next;
}
