#ifndef ML_DSA_H
#define ML_DSA_H

#include <stddef.h>
#include <stdint.h>

#define MLDSA65_PUBLICKEYBYTES 1952
#define MLDSA65_SECRETKEYBYTES 4032
#define MLDSA65_SIGBYTES       3309

typedef enum {
    MLDSA_SUCCESS = 0,
    MLDSA_ERROR_INVALID_SIGNATURE = -1,
    MLDSA_ERROR_VERIFICATION_FAILED = -2,
    MLDSA_ERROR_RNG = -3
} mldsa_status_t;

mldsa_status_t crypto_sign_keypair(
    uint8_t pk[MLDSA65_PUBLICKEYBYTES],
    uint8_t sk[MLDSA65_SECRETKEYBYTES]
);

mldsa_status_t crypto_sign_signature(
    uint8_t sig[MLDSA65_SIGBYTES],
    size_t *siglen,
    const uint8_t *msg,
    size_t msglen,
    const uint8_t sk[MLDSA65_SECRETKEYBYTES]
);

mldsa_status_t crypto_sign_verify(
    const uint8_t sig[MLDSA65_SIGBYTES],
    size_t siglen,
    const uint8_t *msg,
    size_t msglen,
    const uint8_t pk[MLDSA65_PUBLICKEYBYTES]
);

#endif // ML_DSA_H
