#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

void ble_crypto_f4(const uint8_t u[32], const uint8_t v[32],
                   const uint8_t x[16], uint8_t z,
                   uint8_t confirm_out[16]) {
    uint8_t msg[65];
    memcpy(&msg[0], u, 32);
    memcpy(&msg[32], v, 32);
    msg[64] = z;

    ble_crypto_aes_cmac(x, msg, sizeof(msg), confirm_out);
}

uint32_t ble_crypto_g2(const uint8_t u[32], const uint8_t v[32],
                       const uint8_t x[16], const uint8_t y[16]) {
    uint8_t msg[80];
    uint8_t mac[16];

    memcpy(&msg[0], u, 32);
    memcpy(&msg[32], v, 32);
    memcpy(&msg[64], y, 16);

    ble_crypto_aes_cmac(x, msg, sizeof(msg), mac);

    uint32_t val = (uint32_t)mac[0] |
                   ((uint32_t)mac[1] << 8) |
                   ((uint32_t)mac[2] << 16) |
                   ((uint32_t)mac[3] << 24);

    return val % 1000000;
}
