#include <stdint.h>
#include <stdio.h>

// GF(2^4) з примітивним x^4 + x + 1 (0b10011): 15 ненульових елементів.
#define M 4
#define N 15
static uint8_t exp_of[N];      // exp_of[i] = alpha^i як 4-бітовий вектор
static uint8_t log_of[N + 1];  // log_of[v] = i, де alpha^i = v

static void gf_init(void) {
    uint16_t v = 1;
    for (int i = 0; i < N; i++) {
        exp_of[i] = (uint8_t)v;
        log_of[v] = (uint8_t)i;
        v <<= 1;
        if (v & (1 << M)) v ^= 0b10011;   // згорнути назад у поле
    }
}
static uint8_t gf_mul(uint8_t a, uint8_t b) {
    if (!a || !b) return 0;
    return exp_of[(log_of[a] + log_of[b]) % N];   // множення = додавання показників
}
static uint8_t gf_inv(uint8_t a) {                // ділення через від'ємний показник
    return exp_of[(N - log_of[a]) % N];
}

int main(void) {
    gf_init();

    // Помилки на позиціях 3 і 10  →  e(x) = x^3 + x^10.
    // Синдром Sj = r(alpha^j) = alpha^(3j) + alpha^(10j)  (дані занулюються).
    uint8_t S[5];
    for (int j = 1; j <= 4; j++)
        S[j] = exp_of[(3 * j) % N] ^ exp_of[(10 * j) % N];
    printf("S1..S4 = %d %d %d %d\n", S[1], S[2], S[3], S[4]);

    // Локатор для двох помилок: sigma(x) = 1 + s1*x + s2*x^2.
    uint8_t s1 = S[1];
    uint8_t s1cube = gf_mul(gf_mul(S[1], S[1]), S[1]);   // S1^3
    uint8_t s2 = gf_mul(S[3] ^ s1cube, gf_inv(S[1]));    // (S3 + S1^3)/S1

    // Пошук Ченя: корінь sigma у x = alpha^(-i)  →  помилка на позиції i.
    printf("позиції помилок:");
    for (int i = 0; i < N; i++) {
        uint8_t xi = exp_of[(N - i) % N];               // alpha^(-i)
        uint8_t val = 1 ^ gf_mul(s1, xi) ^ gf_mul(s2, gf_mul(xi, xi));
        if (val == 0) printf(" %d", i);
    }
    printf("\n");
    return 0;                          // друкує: S1..S4 = 15 10 11 8 / позиції: 3 10
}
