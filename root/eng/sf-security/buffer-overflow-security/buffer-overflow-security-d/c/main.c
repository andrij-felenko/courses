#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define USERNAME_MAX_CAPACITY 64

// Захищена функція копіювання з контролем меж буфера
bool copy_username_bounded(char *dest, size_t dest_capacity, const char *src) {
    if (!dest || !src || dest_capacity == 0) {
        return false;
    }

    // Використання snprintf гарантує запис не більше dest_capacity байтів
    // і обов'язкову наявність завершального нуль-термінатора '\0'
    int written = snprintf(dest, dest_capacity, "%s", src);

    // Якщо довжина джерела перевищує або дорівнює місткості — відбулося обрізання
    if (written < 0 || (size_t)written >= dest_capacity) {
        // Очищаємо цільовий буфер для запобігання використанню обрізаних даних
        dest[0] = '\0';
        return false;
    }

    return true;
}
