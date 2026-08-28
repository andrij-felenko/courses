#include <stdio.h>
#include <stdint.h>

typedef unsigned __int128 u128;

// x mod (2^p − 1) — самими зсувами й додаваннями, без ділення
static u128 mod_mersenne(u128 x, unsigned p) {
    u128 mask = ((u128)1 << p) - 1;        // молодші p бітів
    while (x >> p)                          // поки лишилися старші за p біти
        x = (x >> p) + (x & mask);          // hi + lo   (бо 2^p ≡ 1)
    if (x == mask)                          // єдиний окремий випадок:
        x = 0;                              // рівно 2^p − 1 — це той самий 0
    return x;
}

// тест Люка–Лемера для 2^p − 1  (помірне p: 2^p вміщається в 64 біти)
int lucas_lehmer(unsigned p) {
    u128 M = ((u128)1 << p) - 1;
    u128 s = 4;
    for (unsigned k = 0; k < p - 2; k++) {
        u128 sq = mod_mersenne(s * s, p);   // піднести до квадрата й звести
        s = sq >= 2 ? sq - 2 : sq + M - 2;  // відняти 2 без переповнення
    }
    return s == 0;
}

int main(void) {
    unsigned ps[] = {3, 5, 7, 11, 13, 17, 19, 31};
    for (int i = 0; i < 8; i++) {
        unsigned p = ps[i];
        printf("p=%2u  M=%llu  %s\n", p,
               (unsigned long long)(((u128)1 << p) - 1),
               lucas_lehmer(p) ? "просте ✓" : "складене");
    }
    return 0;
}
