void frng_generate_safe(frng *r, uint8_t *out, size_t n) {
    if (getpid() != r->pid) {           /* нас форкнули — стан успадкований */
        uint8_t fresh[32];
        os_getrandom(fresh, 32);        /* свіже насіння від ядра */
        frng_reseed(r, fresh, 32);
        secure_wipe(fresh, sizeof fresh);
        r->pid = getpid();
    }
    frng_generate(r, out, n);
}
