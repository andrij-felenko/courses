#include <stdint.h>
#include <stddef.h>

// Кодер: k пакетів даних по L байтів → один пакет парності = XOR усіх.
void fec_xor(const uint8_t *pkt[], int k, size_t L, uint8_t *parity) {
    for (size_t i = 0; i < L; i++) {
        uint8_t x = 0;
        for (int j = 0; j < k; j++)
            x ^= pkt[j][i];
        parity[i] = x;               // байт парності на позиції i
    }
}

// Відновлення зниклого пакета — та сама дія: XOR усіх, що вціліли.
// have[] = k пакетів, які реально дійшли (k−1 даних + пакет парності).
void fec_recover(const uint8_t *have[], int k, size_t L, uint8_t *lost) {
    fec_xor(have, k, L, lost);       // тому окрема функція й не потрібна
}
