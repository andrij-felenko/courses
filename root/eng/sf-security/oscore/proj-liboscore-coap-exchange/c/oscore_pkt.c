#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* Формування додаткових даних автентифікації AAD для AEAD-шифрування */
size_t oscore_build_aad(const uint8_t *header, size_t hdr_len, uint8_t *aad_out) {
    /* Упаковка версії, коду CoAP та параметрів OSCORE у блок AAD */
    aad_out[0] = 0x84; /* Масив CBOR із 4 елементів */
    aad_out[1] = 0x01; /* Версія OSCORE v1 */
    memcpy(aad_out + 2, header, hdr_len);
    
    return 2 + hdr_len;
}

/* Запакування опції OSCORE Option (Option 9) */
size_t oscore_encode_option(uint64_t seq, const uint8_t *kid, size_t kid_len, uint8_t *opt_out) {
    uint8_t flag = 0x09; /* Прапорці: Partial IV присутній (b0), KID присутній (b3) */
    size_t idx = 0;
    
    opt_out[idx++] = flag;
    
    /* Запис Partial IV (Sequence Number у мережевому порядку байтів) */
    opt_out[idx++] = (seq >> 8) & 0xFF;
    opt_out[idx++] = seq & 0xFF;
    
    /* Запис KID */
    memcpy(opt_out + idx, kid, kid_len);
    idx += kid_len;
    
    printf("[OSCORE Packet] Опцію OSCORE запаковано. Довжина: %zu байтів.\n", idx);
    return idx;
}
