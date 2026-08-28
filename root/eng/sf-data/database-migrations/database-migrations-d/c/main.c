#include <stdio.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    char column_name[32];
    char data_type[16];
    bool is_nullable;
} column_schema_t;

bool validate_schema_compatibility(column_schema_t *current_schema, size_t count, const char *required_col) {
    for (size_t i = 0; i < count; ++i) {
        if (strcmp(current_schema[i].column_name, required_col) == 0) {
            printf("Колонка %s знайдена в схемі бази даних.\n", required_col);
            return true;
        }
    }
    fprintf(stderr, "Помилка несумісності: колонка %s відсутня!\n", required_col);
    return false;
}
