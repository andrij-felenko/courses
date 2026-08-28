// main.c — Явне завантаження версіонованих символів у C
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

// Оголошення типів покажчиків на функції для двох версій ABI
typedef int (*foo_v1_fn)(int);
typedef int (*foo_v2_fn)(int, int);

void run_dynamic_test(void) {
    // 1. Відкриваємо спільну бібліотеку за допомогою dlopen
    void* handle = dlopen("libfoo.so.1", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "Помилка завантаження бібліотеки: %s\n", dlerror());
        return;
    }

    // Очищаємо попередні помилки dlfcn
    dlerror();

    // 2. Отримуємо покажчик на старий ABI v1.0 через dlvsym
    foo_v1_fn func_v1 = (foo_v1_fn)dlvsym(handle, "foo_process", "LIBFOO_1.0");
    char* error = dlerror();
    if (error != NULL) {
        fprintf(stderr, "Помилка отримання символу v1.0: %s\n", error);
    } else {
        int res1 = func_v1(42);
        printf("[C Client] Виклик foo_process@LIBFOO_1.0(42) повернув: %d\n", res1);
    }

    // 3. Отримуємо покажчик на новий ABI v2.0 через dlvsym
    foo_v2_fn func_v2 = (foo_v2_fn)dlvsym(handle, "foo_process", "LIBFOO_2.0");
    error = dlerror();
    if (error != NULL) {
        fprintf(stderr, "Помилка отримання символу v2.0: %s\n", error);
    } else {
        int res2 = func_v2(42, 100);
        printf("[C Client] Виклик foo_process@@LIBFOO_2.0(42, 100) повернув: %d\n", res2);
    }

    // 4. Закриваємо дескриптор бібліотеки
    dlclose(handle);
}
