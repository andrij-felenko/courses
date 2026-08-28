#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

// Перелік підтримуваних типів даних
typedef enum {
    TYPE_INT32,
    TYPE_DOUBLE,
    TYPE_STRING,
    TYPE_BOOL
} FieldType;

// Дескриптор одного поля структури
typedef struct {
    const char* name;
    FieldType   type;
    size_t      offset;
    size_t      size;
} FieldMeta;

// Дескриптор усієї структури (метаклас)
typedef struct {
    const char*      struct_name;
    size_t           total_size;
    const FieldMeta* fields;
    size_t           field_count;
} StructMeta;

// Цільова структура прикладних даних
typedef struct {
    int32_t id;
    char    username[32];
    double  balance;
    bool    is_active;
} UserProfile;

// Таблиця метаданих для UserProfile
static const FieldMeta USER_PROFILE_FIELDS[] = {
    { "id",        TYPE_INT32,  offsetof(UserProfile, id),        sizeof(int32_t) },
    { "username",  TYPE_STRING, offsetof(UserProfile, username),  32 },
    { "balance",   TYPE_DOUBLE, offsetof(UserProfile, balance),   sizeof(double) },
    { "is_active", TYPE_BOOL,   offsetof(UserProfile, is_active), sizeof(bool) }
};

static const StructMeta USER_PROFILE_META = {
    .struct_name = "UserProfile",
    .total_size  = sizeof(UserProfile),
    .fields      = USER_PROFILE_FIELDS,
    .field_count = sizeof(USER_PROFILE_FIELDS) / sizeof(USER_PROFILE_FIELDS[0])
};

// Універсальна функція серіалізації в JSON за метаданими
void serialize_to_json(const void* object_ptr, const StructMeta* meta, char* buffer, size_t max_len) {
    size_t written = snprintf(buffer, max_len, "{\n  \"_type\": \"%s\",\n", meta->struct_name);
    const uint8_t* base = (const uint8_t*)object_ptr;

    for (size_t i = 0; i < meta->field_count; ++i) {
        const FieldMeta* field = &meta->fields[i];
        const void* field_addr = base + field->offset;

        written += snprintf(buffer + written, max_len - written, "  \"%s\": ", field->name);

        switch (field->type) {
            case TYPE_INT32: {
                int32_t val = *(const int32_t*)field_addr;
                written += snprintf(buffer + written, max_len - written, "%d", val);
                break;
            }
            case TYPE_DOUBLE: {
                double val = *(const double*)field_addr;
                written += snprintf(buffer + written, max_len - written, "%.2f", val);
                break;
            }
            case TYPE_STRING: {
                const char* str = (const char*)field_addr;
                written += snprintf(buffer + written, max_len - written, "\"%s\"", str);
                break;
            }
            case TYPE_BOOL: {
                bool val = *(const bool*)field_addr;
                written += snprintf(buffer + written, max_len - written, "%s", val ? "true" : "false");
                break;
            }
        }

        if (i + 1 < meta->field_count) {
            written += snprintf(buffer + written, max_len - written, ",\n");
        } else {
            written += snprintf(buffer + written, max_len - written, "\n");
        }
    }
    snprintf(buffer + written, max_len - written, "}");
}

int main(void) {
    UserProfile user = {
        .id = 1042,
        .username = "andrij_f",
        .balance = 250.75,
        .is_active = true
    };

    char json_output[512];
    serialize_to_json(&user, &USER_PROFILE_META, json_output, sizeof(json_output));
    printf("%s\n", json_output);

    return 0;
}
