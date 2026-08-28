#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <stdint.h>

/* Оголошення покажчиків на функції за C-сигнатурами */
typedef struct engine_ctx_t engine_ctx_t;
typedef int (*fn_engine_create)(const char*, engine_ctx_t**);
typedef void (*fn_engine_destroy)(engine_ctx_t*);
typedef int (*fn_engine_process)(engine_ctx_t*, const uint8_t*, size_t, uint8_t*, size_t*);
typedef const char* (*fn_engine_get_last_error)(void);

int main(void) {
    void* lib_handle = dlopen("./libengine.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib_handle) {
        fprintf(stderr, "Не вдалося завантажити бібліотеку: %s\n", dlerror());
        return EXIT_FAILURE;
    }

    /* Отримання адрес неспотворених C-символів */
    fn_engine_create p_create = (fn_engine_create)dlsym(lib_handle, "engine_create");
    fn_engine_destroy p_destroy = (fn_engine_destroy)dlsym(lib_handle, "engine_destroy");
    fn_engine_process p_process = (fn_engine_process)dlsym(lib_handle, "engine_process");
    fn_engine_get_last_error p_error = (fn_engine_get_last_error)dlsym(lib_handle, "engine_get_last_error");

    if (!p_create || !p_destroy || !p_process || !p_error) {
        fprintf(stderr, "Помилка пошуку C-символів у бібліотеці: %s\n", dlerror());
        dlclose(lib_handle);
        return EXIT_FAILURE;
    }

    engine_ctx_t* ctx = NULL;
    if (p_create("XOR-FAST", &ctx) != 0) {
        fprintf(stderr, "Помилка ініціалізації: %s\n", p_error());
        dlclose(lib_handle);
        return EXIT_FAILURE;
    }

    const uint8_t msg[] = { 0xAA, 0xBB, 0xCC };
    uint8_t out[16];
    size_t out_len = sizeof(out);

    p_process(ctx, msg, sizeof(msg), out, &out_len);
    printf("[Dynamic C] Успішно виконано динамічний виклик. Довжина: %zu\n", out_len);

    p_destroy(ctx);
    dlclose(lib_handle);
    return EXIT_SUCCESS;
}
