/* dlfcn_demo.c — Приклад динамічного завантаження плагіна мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

typedef double (*math_func_t)(double);

int main(void) {
    /* Відкриваємо математичну бібліотеку */
    void *handle = dlopen("libm.so.6", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "dlopen error: %s\n", dlerror());
        return 1;
    }

    /* Очищаємо існуючі помилки */
    dlerror();

    /* Шукаємо функцію cos */
    math_func_t cos_fn = (math_func_t)dlsym(handle, "cos");
    const char *dlsym_err = dlerror();
    if (dlsym_err != NULL) {
        fprintf(stderr, "dlsym error: %s\n", dlsym_err);
        dlclose(handle);
        return 1;
    }

    /* Отримуємо інформацію про символ через dladdr */
    Dl_info info;
    if (dladdr((void*)cos_fn, &info)) {
        printf("Symbol 'cos' found in file: %s at base address: %p\n",
               info.dli_fname, info.dli_fbase);
    }

    /* Викликаємо знайдену функцію */
    double result = cos_fn(3.141592653589793 / 3.0);
    printf("cos(pi/3) = %f\n", result);

    /* Закриваємо хендл */
    dlclose(handle);
    return 0;
}
