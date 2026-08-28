#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

void ble_crypto_f5(const uint8_t dhkey[32],
                   const uint8_t na[16], const uint8_t nb[16],
                   uint8_t a1_type, const uint8_t a1_addr[6],
                   uint8_t a2_type, const uint8_t a2_addr[6],
                   uint8_t mackey_out[16], uint8_t ltk_out[16]) {
    static const uint8_t SALT[16] = {
        0xBE, 0x83, 0x60, 0x5A, 0xDB, 0x0B, 0x37, 0x60,
        0x38, 0xA5, 0xF5, 0xAA, 0x91, 0x83, 0x88, 0x6C
    };

    uint8_t w[16];
    uint8_t msg[53];

    /* W = AES-CMAC_SALT(DHKey) */
    ble_crypto_aes_cmac(SALT, dhkey, 32, w);

    msg[1] = 'b'; msg[2] = 't'; msg[3] = 'l'; msg[4] = 'e';
    memcpy(&msg[5], na, 16);
    memcpy(&msg[21], nb, 16);
    msg[37] = a1_type;
    memcpy(&msg[38], a1_addr, 6);
    msg[44] = a2_type;
    memcpy(&msg[45], a2_addr, 6);
    msg[51] = 0x00;
    msg[52] = 0x01; /* 256 бітів довжини */

    /* Генерація MacKey (Counter = 0) */
    msg[0] = 0x00;
    ble_crypto_aes_cmac(w, msg, sizeof(msg), mackey_out);

    /* Генерація LTK (Counter = 1) */
    msg[0] = 0x01;
    ble_crypto_aes_cmac(w, msg, sizeof(msg), ltk_out);
}
