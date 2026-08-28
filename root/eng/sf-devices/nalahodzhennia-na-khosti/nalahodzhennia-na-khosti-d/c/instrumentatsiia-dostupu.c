/* Інструментований компілятором C-код */
void store_val_instrumented(int *address, int val) {
    int8_t *shadow = (int8_t*)(((uintptr_t)address >> 3) + 0x7fff8000);
    int8_t shadow_val = *shadow;
    if (shadow_val != 0) {
        int8_t last_byte = (int8_t)((uintptr_t)address & 7);
        if (last_byte >= shadow_val) {
            __builtin_trap(); /* Негайний краш і звіт ASan */
        }
    }
    *address = val;
}
