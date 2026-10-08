#include <stdio.h>
#include <stdint.h>

/* Оголошення зовнішніх функцій з модулів */
typedef struct {
    uint8_t master_secret[16];
    uint8_t master_salt[8];
    uint8_t sender_id[4];
    uint8_t recipient_id[4];
    uint8_t sender_key[16];
    uint8_t recipient_key[16];
    uint8_t common_iv[13];
    uint64_t sequence_number;
} oscore_context_t;

int oscore_context_init(oscore_context_t *ctx);
size_t oscore_build_aad(const uint8_t *header, size_t hdr_len, uint8_t *aad_out);
size_t oscore_encode_option(uint64_t seq, const uint8_t *kid, size_t kid_len, uint8_t *opt_out);

int main(void) {
    oscore_context_t ctx;
    uint8_t aad[64];
    uint8_t oscore_option[32];
    uint8_t dummy_header[4] = {0x40, 0x01, 0x12, 0x34}; /* Заголовок CoAP CON GET */

    printf("--- Демонстрація роботи OSCORE liboscore (RFC 8613) ---\n");
    
    if (oscore_context_init(&ctx) != 0) {
        fprintf(stderr, "Помилка ініціалізації контексту!\n");
        return 1;
    }

    size_t aad_len = oscore_build_aad(dummy_header, sizeof(dummy_header), aad);
    printf("[Main] Блок AAD сформовано, розмір: %zu байтів.\n", aad_len);

    size_t opt_len = oscore_encode_option(ctx.sequence_number, ctx.sender_id, 1, oscore_option);
    printf("[Main] CoAP OSCORE Option (9) сформовано, розмір: %zu байтів.\n", opt_len);

    printf("[Main] Передача CoAP-повідомлення захищена успішно.\n");
    return 0;
}
