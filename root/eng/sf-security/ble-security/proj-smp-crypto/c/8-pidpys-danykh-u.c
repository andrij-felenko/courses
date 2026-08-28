#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

/**
 * @brief Обчислення підпису даних для кадру ATT Signed Write
 * @param csrk 128-бітний ключ підпису CSRK (16 байтів)
 * @param att_pdu Масив корисного навантаження кадру ATT
 * @param pdu_len Довжина кадру ATT без підпису
 * @param sign_counter 32-бітний поточний лічильник підпису
 * @param signature_out 12-байтний буфер для результату: [0..7]=MAC, [8..11]=SignCounter
 */
void ble_att_sign_data(const uint8_t csrk[16], const uint8_t *att_pdu, size_t pdu_len,
                       uint32_t sign_counter, uint8_t signature_out[12]) {
    uint8_t buffer[256];
    uint8_t mac_full[16];

    /* Формування повідомлення: ATT_PDU || SignCounter */
    memcpy(&buffer[0], att_pdu, pdu_len);
    buffer[pdu_len + 0] = (uint8_t)(sign_counter & 0xFF);
    buffer[pdu_len + 1] = (uint8_t)((sign_counter >> 8) & 0xFF);
    buffer[pdu_len + 2] = (uint8_t)((sign_counter >> 16) & 0xFF);
    buffer[pdu_len + 3] = (uint8_t)((sign_counter >> 24) & 0xFF);

    ble_crypto_aes_cmac(csrk, buffer, pdu_len + 4, mac_full);

    /* Молодші 8 байтів MAC (64 біти) */
    memcpy(&signature_out[0], &mac_full[0], 8);
    /* Додавання SignCounter */
    memcpy(&signature_out[8], &buffer[pdu_len], 4);
}
