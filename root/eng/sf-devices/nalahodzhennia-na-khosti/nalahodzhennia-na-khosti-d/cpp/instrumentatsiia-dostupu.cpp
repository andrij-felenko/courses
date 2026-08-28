// Інструментований компілятором C++ код
void store_val_instrumented(int *address, int val) noexcept {
    auto *shadow = reinterpret_cast<int8_t*>(((reinterpret_cast<uintptr_t>(address) >> 3) + 0x7fff8000));
    const int8_t shadow_val = *shadow;
    if (shadow_val != 0) {
        const auto last_byte = static_cast<int8_t>(reinterpret_cast<uintptr_t>(address) & 7);
        if (last_byte >= shadow_val) {
            __builtin_trap(); // Негайний краш і звіт ASan
        }
    }
    *address = val;
}
