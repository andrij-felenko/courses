typedef void (*init_func_t)(void);

extern init_func_t __init_array_start[];
extern init_func_t __init_array_end[];

void call_global_constructors_c(void) {
    size_t count = (size_t)(__init_array_end - __init_array_start);
    for (size_t i = 0; i < count; ++i) {
        __init_array_start[i]();
    }
}
