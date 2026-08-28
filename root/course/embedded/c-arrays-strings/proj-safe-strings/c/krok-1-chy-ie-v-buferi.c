#include <string.h>
#include <stdbool.h>
#include <stddef.h>

// Чи є в перших size байтах буфера завершальний '\0'?
// Якщо так — out_len дістає довжину рядка (як strlen, але БЕЗ ризику
// вибігти за межу). Якщо ні — буфер НЕ рядок, повертаємо false.
bool buf_is_string(const char *buf, size_t size, size_t *out_len) {
    const char *nul = memchr(buf, '\0', size);  // шукаємо '\0', не далі size байтів
    if (nul == NULL) {
        return false;               // термінатора немає — це не рядок, крапка
    }
    if (out_len != NULL) {
        *out_len = (size_t)(nul - buf);  // байтів ДО '\0' — це і є довжина
    }
    return true;
}
