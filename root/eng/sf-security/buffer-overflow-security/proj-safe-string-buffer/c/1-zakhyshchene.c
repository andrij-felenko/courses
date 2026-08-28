#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define MAX_BUFFER_SIZE 64

// Безпечне копіювання з явним контролем довжини та гарантією нуль-термінатора
bool safe_copy_string(char *dest, size_t dest_cap, const char *src) {
    if (!dest || !src || dest_cap == 0) {
        return false;
    }
    
    size_t src_len = strlen(src);
    // Перевірка: довжина рядка разом із нульовим байтом не повинна перевищувати місткість
    if (src_len >= dest_cap) {
        // Дані перевищують місткість буфера — відкидаємо копіювання
        return false;
    }
    
    memcpy(dest, src, src_len);
    dest[src_len] = '\0';
    return true;
}

int main(void) {
    char destination[MAX_BUFFER_SIZE];
    const char *untrusted_input = "Untrusted input string payload";

    if (safe_copy_string(destination, sizeof(destination), untrusted_input)) {
        printf("Успішно скопійовано: %s\n", destination);
    } else {
        printf("Помилка: вхідні дані перевищують розмір буфера!\n");
    }
    return 0;
}
