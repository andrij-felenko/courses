#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

/**
 * @brief Функція f6 для обчислення контрольного значення DHKey Check
 */
void ble_crypto_f6(const uint8_t mackey[16],
                   const uint8_t n1[16], const uint8_t n2[16],
                   const uint8_t r[16],
                   const uint8_t iocap[3],
                   uint8_t a1_type, const uint8_t a1_addr[6],
                   uint8_t a2_type, const uint8_t a2_addr[6],
                   uint8_t check_out[16]) {
    uint8_t msg[65];

    /* Повідомлення: N1(16) || N2(16) || R(16) || IOcap(3) || A1_type(1) || A1_addr(6) || A2_type(1) || A2_addr(6) */
    memcpy(&msg[0], n1, 16);
    memcpy(&msg[16], n2, 16);
    memcpy(&msg[32], r, 16);
    memcpy(&msg[48], iocap, 3);
    msg[51] = a1_type;
    memcpy(&msg[52], a1_addr, 6);
    msg[58] = a2_type;
    memcpy(&msg[59], a2_addr, 6);

    ble_crypto_aes_cmac(mackey, msg, sizeof(msg), check_out);
}
