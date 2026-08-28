#include <string.h>
#include <stdbool.h>

bool validate_if_range(const char *if_range_header, const char *current_etag, const char *last_modified_date) {
    if (!if_range_header || *if_range_header == '\0') {
        return true; /* Заголовок відсутній: обробляємо Range безумовно */
    }

    /* Відкидаємо слабкі валідатори за RFC 9110 */
    if (strncmp(if_range_header, "W/", 2) == 0) {
        return false;
    }

    /* Перевірка сильного ETag */
    if (*if_range_header == '"') {
        return current_etag && (strcmp(if_range_header, current_etag) == 0);
    }

    /* Перевірка HTTP-дати останньої модифікації */
    if (last_modified_date && strcmp(if_range_header, last_modified_date) == 0) {
        return true;
    }

    return false;
}
