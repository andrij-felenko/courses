#include <stdint.h>
#include <string.h>

extern void aes128_ecb_encrypt(const uint8_t key[16], const uint8_t input[16], uint8_t output[16]);

/**
 * @brief Функція диверсифікації ключів s1 (STK Generation)
 * @param tk Тимчасовий ключ (16 байтів)
 * @param r1 Випадкове число відповідача Srand (16 байтів)
 * @param r2 Випадкове число ініціатора Mrand (16 байтів)
 * @param stk_out Вихідний короткостроковий ключ STK (16 байтів)
 */
void ble_crypto_s1(const uint8_t tk[16], const uint8_t r1[16], const uint8_t r2[16], uint8_t stk_out[16]) {
    uint8_t r_prime[16];
    
    /* r' = молодші 8 байтів r1 || молодші 8 байтів r2 */
    memcpy(&r_prime[0], &r1[0], 8);
    memcpy(&r_prime[8], &r2[0], 8);

    /* STK = AES-128_TK(r') */
    aes128_ecb_encrypt(tk, r_prime, stk_out);
}

/**
 * @brief Функція підтвердження c1 для LE Legacy Pairing
 */
void ble_crypto_c1(const uint8_t tk[16], const uint8_t r1[16],
                   const uint8_t preq[7], const uint8_t pres[7],
                   uint8_t iat, uint8_t rat,
                   const uint8_t ia[6], const uint8_t ra[6],
                   uint8_t confirm_out[16]) {
    uint8_t p1[16];
    uint8_t p2[16];
    uint8_t t1[16];
    uint8_t t2[16];

    /* Формування вектора p1: pres(7) || preq(7) || rat(1) || iat(1) */
    memcpy(&p1[0], pres, 7);
    memcpy(&p1[7], preq, 7);
    p1[14] = rat;
    p1[15] = iat;

    /* Формування вектора p2: padding(4) || ia(6) || padding(4) || ra(6) */
    memset(p2, 0, 16);
    memcpy(&p2[0], ra, 6);
    memcpy(&p2[6], ia, 6);

    /* Перший раунд: t1 = AES_TK(r ^ p1) */
    for (int i = 0; i < 16; ++i) {
        t1[i] = r1[i] ^ p1[i];
    }
    aes128_ecb_encrypt(tk, t1, t2);

    /* Другий раунд: confirm = AES_TK(t2 ^ p2) */
    for (int i = 0; i < 16; ++i) {
        t2[i] = t2[i] ^ p2[i];
    }
    aes128_ecb_encrypt(tk, t2, confirm_out);
}
