#include <stdint.h>

// ZCR із мертвою зоною: перетином вважаємо лише впевнений перехід через ±delta.
// Це гасить фальшиві «клацання» шуму коло самого нуля.
int zcr_hysteresis(const int16_t *frame, int N, int16_t delta) {
    int count = 0;
    int sign  = 0;                        // −1, +1 або 0 (ще не визначено)
    for (int i = 0; i < N; i++) {
        int s;
        if (frame[i] >  delta)      s =  1;    // впевнено вище зони
        else if (frame[i] < -delta) s = -1;    // впевнено нижче зони
        else                        continue;  // у мертвій зоні — знак не міняємо
        if (sign != 0 && s != sign) count++;   // знак реально перевернувся
        sign = s;
    }
    return count;
}
