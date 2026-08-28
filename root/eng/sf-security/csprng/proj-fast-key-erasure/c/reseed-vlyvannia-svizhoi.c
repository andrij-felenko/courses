void frng_reseed(frng *r, const uint8_t *seed, size_t slen) {
    uint8_t block[64];
    size_t  off = 0;

    do {
        size_t chunk = (slen - off) < 32 ? (slen - off) : 32;
        for (size_t i = 0; i < chunk; i++)
            r->key[i] ^= seed[off + i];      /* підмішати шматок насіння */
        chacha20_block(r->key, 0, block);    /* односторонньо перемішати */
        memcpy(r->key, block, 32);           /* новий ключ = ChaCha(суміш) */
        off += chunk;
    } while (off < slen);

    secure_wipe(block, sizeof block);
}
