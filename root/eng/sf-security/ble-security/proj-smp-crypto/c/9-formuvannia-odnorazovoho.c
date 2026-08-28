#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/**
 * @brief Побудова 13-байтного вектора Nonce для канального рівня Link Layer
 * @param packet_counter 39-бітне значення лічильника пакетів (uint64_t)
 * @param is_master_to_slave true, якщо пакет надсилає Master; false для Slave
 * @param iv 64-бітний вектор ініціалізації (8 байтів)
 * @param nonce_out 13-байтний вихідний масив
 */
void ble_ll_build_nonce(uint64_t packet_counter, bool is_master_to_slave,
                        const uint8_t iv[8], uint8_t nonce_out[13]) {
    /* Байти 0..4: 39 бітів лічильника пакетів у порядку Little-Endian */
    nonce_out[0] = (uint8_t)(packet_counter & 0xFF);
    nonce_out[1] = (uint8_t)((packet_counter >> 8) & 0xFF);
    nonce_out[2] = (uint8_t)((packet_counter >> 16) & 0xFF);
    nonce_out[3] = (uint8_t)((packet_counter >> 24) & 0xFF);
    nonce_out[4] = (uint8_t)((packet_counter >> 32) & 0x7F);

    /* Байт 4, старший біт (біт 7): Direction Bit */
    if (is_master_to_slave) {
        nonce_out[4] |= 0x80;
    }

    /* Байти 5..12: 64 біти вектора IV */
    memcpy(&nonce_out[5], iv, 8);
}
