#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    TYPE_INT32,
    TYPE_INT64,
    TYPE_STRING,
    TYPE_BOOLEAN
} FieldType;

typedef struct {
    char name[64];
    FieldType type;
    bool has_default;
} SchemaField;

typedef struct {
    SchemaField fields[32];
    size_t field_count;
} RecordSchema;

bool is_type_compatible(FieldType old_t, FieldType new_t) {
    if (old_t == new_t) return true;
    /* Дозволене розширення числових типів: 32-бітний int безпечно читається як 64-бітний long */
    if (old_t == TYPE_INT32 && new_t == TYPE_INT64) return true;
    return false;
}

const SchemaField* find_field(const RecordSchema *schema, const char *name) {
    for (size_t i = 0; i < schema->field_count; ++i) {
        if (strcmp(schema->fields[i].name, name) == 0) {
            return &schema->fields[i];
        }
    }
    return NULL;
}

/* Перевірка зворотної сумісності BACKWARD */
bool validate_backward_compatibility(const RecordSchema *old_schema, const RecordSchema *new_schema, char *error_buf, size_t err_len) {
    for (size_t i = 0; i < new_schema->field_count; ++i) {
        const SchemaField *new_f = &new_schema->fields[i];
        const SchemaField *old_f = find_field(old_schema, new_f->name);

        if (old_f == NULL) {
            /* Поле нове: зобов'язане мати default для старих повідомлень */
            if (!new_f->has_default) {
                snprintf(error_buf, err_len, "Нове поле '%s' не має значення за замовчуванням", new_f->name);
                return false;
            }
        } else {
            /* Поле існувало: перевірка сумісності типів */
            if (!is_type_compatible(old_f->type, new_f->type)) {
                snprintf(error_buf, err_len, "Несумісна зміна типу для поля '%s'", new_f->name);
                return false;
            }
        }
    }
    return true;
}
