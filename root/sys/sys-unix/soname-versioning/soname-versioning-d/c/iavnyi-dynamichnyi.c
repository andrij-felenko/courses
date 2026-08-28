#define _GNU_SOURCE
#include <stdio.h>
#include <dlfcn.h>

void execute_plugin(void) {
    void* handle = dlopen("libfoo.so.1", RTLD_LAZY);
    if (!handle) return;

    // Отримання конкретної версії символу через dlvsym
    typedef int (*func_v1_t)(int);
    func_v1_t func = (func_v1_t)dlvsym(handle, "foo_process", "LIBFOO_1.0");
    if (func) {
        int res = func(42);
        printf("Результат виклику v1: %d\n", res);
    }

    dlclose(handle);
}
