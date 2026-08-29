#ifndef HMAC_SHA256_H
#define HMAC_SHA256_H

#include <stddef.h>
#include <stdint.h>

#include "sha256.h"

#define HMAC_SHA256_TAG_SIZE SHA256_DIGEST_SIZE

/*
 * HMAC-SHA256 за RFC 2104. Ключ довільної довжини: коротший доповнюється
 * нулями до блоку, довший за 64 байти спершу хешується.
 *
 * Ніякого динамічного виділення: два блоки по 64 байти на стеку.
 */
void hmac_sha256(const uint8_t *key, size_t key_len,
                 const uint8_t *msg, size_t msg_len,
                 uint8_t out[HMAC_SHA256_TAG_SIZE]);

#endif /* HMAC_SHA256_H */
