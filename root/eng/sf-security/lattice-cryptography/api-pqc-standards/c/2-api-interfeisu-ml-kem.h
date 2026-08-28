#ifndef ML_KEM_H
#define ML_KEM_H

#include <stddef.h>
#include <stdint.h>

#define MLKEM768_PUBLICKEYBYTES  1184
#define MLKEM768_SECRETKEYBYTES  2400
#define MLKEM768_CIPHERTEXTBYTES 1088
#define MLKEM768_BYTES           32

typedef enum {
    MLKEM_SUCCESS = 0,
    MLKEM_ERROR_RNG_FAILED = -1,
    MLKEM_ERROR_INVALID_CIPHERTEXT = -2,
    MLKEM_ERROR_BUFFER_TOO_SMALL = -3,
    MLKEM_ERROR_CORRUPTED_KEY = -4
} mlkem_status_t;

mlkem_status_t crypto_kem_keypair(
    uint8_t pk[MLKEM768_PUBLICKEYBYTES],
    uint8_t sk[MLKEM768_SECRETKEYBYTES]
);

mlkem_status_t crypto_kem_enc(
    uint8_t ct[MLKEM768_CIPHERTEXTBYTES],
    uint8_t ss[MLKEM768_BYTES],
    const uint8_t pk[MLKEM768_PUBLICKEYBYTES]
);

mlkem_status_t crypto_kem_dec(
    uint8_t ss[MLKEM768_BYTES],
    const uint8_t ct[MLKEM768_CIPHERTEXTBYTES],
    const uint8_t sk[MLKEM768_SECRETKEYBYTES]
);

#endif // ML_KEM_H
