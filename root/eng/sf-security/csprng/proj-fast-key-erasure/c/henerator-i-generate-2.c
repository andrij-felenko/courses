/* Надійне стирання — memset оптимізатор має право викинути (див. пастки). */
static void secure_wipe(void *p, size_t n) {
    volatile uint8_t *v = (volatile uint8_t *)p;
    while (n--) *v++ = 0;
}

void frng_generate(frng *r, uint8_t *out, size_t n) {
    uint8_t  block[64];
    uint8_t  newkey[32];
    uint32_t counter = 0;

    /* Блок 0: [0..32) — майбутній ключ, [32..64) — початок виходу. */
    chacha20_block(r->key, counter++, block);
    memcpy(newkey, block, 32);
    size_t take = n < 32 ? n : 32;
    memcpy(out, block + 32, take);
    out += take;
    n   -= take;

    /* Решта запиту — цілі блоки того самого потоку (усе ще старий Kᵢ). */
    while (n > 0) {
        chacha20_block(r->key, counter++, block);
        take = n < 64 ? n : 64;
        memcpy(out, block, take);
        out += take;
        n   -= take;
    }

    /* Храповик: новий ключ на місце старого, усе тимчасове — у нуль. */
    memcpy(r->key, newkey, 32);
    secure_wipe(newkey, sizeof newkey);
    secure_wipe(block,  sizeof block);
}
