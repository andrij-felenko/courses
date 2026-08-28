char* shadow = reinterpret_cast<char*>((reinterpret_cast<uintptr_t>(ptr) >> 3) + 0x7fff8000);
int8_t shadow_val = *shadow;

if (shadow_val != 0) {
    // Якщо байт не нульовий, перевіряємо, чи дозволений доступ до останнього байта
    if (shadow_val < 0 || (static_cast<int8_t>(reinterpret_cast<uintptr_t>(ptr) & 7) + 3) >= shadow_val) {
        __asan_report_store4(reinterpret_cast<uintptr_t>(ptr));
    }
}

*ptr = 42;
