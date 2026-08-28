/* Фрагмент виклику глобальних конструкторів у стартап-коді */
extern void (*__init_array_start[])(void) __attribute__((weak));
extern void (*__init_array_end[])(void) __attribute__((weak));

void SystemInit_Cpp() {
    const size_t count = __init_array_end - __init_array_start;
    for (size_t i = 0; i < count; ++i) {
        __init_array_start[i](); // Виклик глобального конструктора
    }
}
