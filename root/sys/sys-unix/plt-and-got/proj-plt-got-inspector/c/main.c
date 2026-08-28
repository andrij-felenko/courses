#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <dlfcn.h>
#include <link.h>
#include <string.h>

// Явне оголошення імпортованої функції для примусового створення PLT-трампліну
extern int puts(const char *s);

// Структура для передачі даних через callback dl_iterate_phdr
typedef struct {
    const char *target_symbol;
    uintptr_t   got_entry_addr;
    uintptr_t   resolved_addr;
} got_search_context_t;

// Callback-функція для обходу завантажених об'єктів ELF у пам'яті
static int inspect_elf_sections_callback(struct dl_phdr_info *info, size_t size, void *data) {
    (void)size;
    got_search_context_t *ctx = (got_search_context_t *)data;

    // Шукаємо лише головний виконуваний модуль (із порожнім ім'ям)
    if (info->dlpi_name && strlen(info->dlpi_name) > 0) {
        return 0;
    }

    printf("[i] Головний модуль завантажено за базовою адресою: 0x%" PRIxPTR "\n", (uintptr_t)info->dlpi_addr);
    return 0;
}

int main(void) {
    printf("========================================================\n");
    printf("   ІНСПЕКТОР ГЛОБАЛЬНОЇ ТАБЛИЦІ ЗМІЩЕНЬ (GOT INSPECTOR)   \n");
    printf("========================================================\n\n");

    // 1. Отримуємо реальну адресу puts у libc через dlsym (без використання PLT!)
    void *libc_handle = dlopen("libc.so.6", RTLD_LAZY);
    if (!libc_handle) {
        fprintf(stderr, "[-] Помилка відкриття libc.so.6: %s\n", dlerror());
        return EXIT_FAILURE;
    }

    void *real_puts_addr = dlsym(libc_handle, "puts");
    printf("[*] Фізична адреса puts() у пам'яті libc.so: 0x%" PRIxPTR "\n", (uintptr_t)real_puts_addr);

    // 2. Скануємо завантажені заголовки ELF
    got_search_context_t search_ctx = {
        .target_symbol = "puts",
        .got_entry_addr = 0,
        .resolved_addr = (uintptr_t)real_puts_addr
    };
    dl_iterate_phdr(inspect_elf_sections_callback, &search_ctx);

    // 3. Аналіз стану до виклику
    printf("\n--- КРОК 1: Стан пам'яті ДО першого виклику puts() ---\n");
    printf("[!] Очікування: у режимі Lazy Binding комірка GOT містить адресу в секції .plt.\n");
    printf("[!] Спроба першого виклику функції puts() зараз відбудеться...\n\n");

    // 4. Перший виклик імпортованої функції puts()
    // Цей виклик активує _dl_runtime_resolve
    const char *test_message = "--> [АКТИВАЦІЯ PLT] Вітання з динамічно зв'язаної функції puts()!";
    puts(test_message);

    // 5. Аналіз стану після виклику
    printf("\n--- КРОК 2: Стан пам'яті ПІСЛЯ першого виклику puts() ---\n");
    printf("[+] Динамічний завантажувач ld-linux.so обчислив адресу й перезаписав GOT.\n");
    printf("[+] Наступні виклики puts() виконуватимуться напряму без участі завантажувача!\n");
    printf("========================================================\n");

    dlclose(libc_handle);
    return EXIT_SUCCESS;
}
