/* Ручна ініціалізація C++ конструкторів у стартовому коді C */
typedef void (*constructor_fn_t)(void);

extern constructor_fn_t __init_array_start[];
extern constructor_fn_t __init_array_end[];

void invoke_global_constructors(void) {
    size_t count = (size_t)(__init_array_end - __init_array_start);
    for (size_t i = 0; i < count; ++i) {
        if (__init_array_start[i] != NULL) {
            __init_array_start[i]();
        }
    }
}
