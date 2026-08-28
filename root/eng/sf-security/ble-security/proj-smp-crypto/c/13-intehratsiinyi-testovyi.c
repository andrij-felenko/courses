#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

extern void ble_crypto_ah(const uint8_t irk[16], const uint8_t prand[3], uint8_t hash_out[3]);
extern bool ble_resolve_rpa(const uint8_t rpa[6], const uint8_t irk[16]);
extern void ble_crypto_f4(const uint8_t u[32], const uint8_t v[32], const uint8_t x[16], uint8_t z, uint8_t confirm_out[16]);
extern uint32_t ble_crypto_g2(const uint8_t u[32], const uint8_t v[32], const uint8_t x[16], const uint8_t y[16]);

bool run_ble_crypto_selftest(void) {
    bool all_passed = true;

    /* 1. Тест ah (RPA Resolution) */
    const uint8_t test_irk[16] = {
        0x9B, 0x7B, 0x63, 0x41, 0x1A, 0x29, 0x55, 0xB1,
        0x8F, 0x8F, 0x86, 0x16, 0xB7, 0xB8, 0x0B, 0x7A
    };
    const uint8_t test_prand[3] = {0x70, 0x81, 0x94};
    uint8_t res_hash[3];

    ble_crypto_ah(test_irk, test_prand, res_hash);
    if (res_hash[0] != 0x05 || res_hash[1] != 0x13 || res_hash[2] != 0x46) {
        printf("[FAIL] ah() test vector mismatch!\n");
        all_passed = false;
    } else {
        printf("[OK] ah() test vector verified.\n");
    }

    return all_passed;
}
