#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>

typedef uint32_t zc_uoffset_t;
typedef int32_t  zc_soffset_t;
typedef uint16_t zc_voffset_t;

/* Структура верифікованого переглядача повідомлення */
typedef struct {
    const uint8_t *buffer;
    size_t size;
    const uint8_t *root_table;
    const uint8_t *vtable;
    zc_voffset_t vtable_size;
    zc_voffset_t table_size;
} zc_reader_t;

/* Безпечне читання скалярів із захистом від порушення вирівнювання */
static inline uint32_t read_u32(const uint8_t *ptr) {
    uint32_t val;
    memcpy(&val, ptr, sizeof(val));
    return val;
}

static inline int32_t read_i32(const uint8_t *ptr) {
    int32_t val;
    memcpy(&val, ptr, sizeof(val));
    return val;
}

static inline uint16_t read_u16(const uint8_t *ptr) {
    uint16_t val;
    memcpy(&val, ptr, sizeof(val));
    return val;
}

/* Ініціалізація та валідація кореневих меж */
bool zc_reader_init(zc_reader_t *reader, const uint8_t *buf, size_t size) {
    if (!reader || !buf || size < sizeof(zc_uoffset_t)) {
        return false;
    }
    reader->buffer = buf;
    reader->size = size;

    /* Читання зсуву кореневої таблиці */
    zc_uoffset_t root_off = read_u32(buf);
    if (root_off >= size || size - root_off < sizeof(zc_soffset_t)) {
        return false;
    }
    reader->root_table = buf + root_off;

    /* Відносний зсув назад до Vtable */
    zc_soffset_t vtable_soff = read_i32(reader->root_table);
    ptrdiff_t vtable_abs_offset = (reader->root_table - buf) - vtable_soff;
    if (vtable_abs_offset < 0 || (size_t)vtable_abs_offset + 4 > size) {
        return false;
    }

    reader->vtable = buf + vtable_abs_offset;
    reader->vtable_size = read_u16(reader->vtable);
    reader->table_size = read_u16(reader->vtable + 2);

    /* Перевірка цілісності Vtable та Table */
    if (reader->vtable_size < 4 || (size_t)vtable_abs_offset + reader->vtable_size > size) {
        return false;
    }
    if (root_off + reader->table_size > size) {
        return false;
    }

    return true;
}

/* Отримання числового поля uint32_t за індексом поля у vtable */
bool zc_get_uint32(const zc_reader_t *reader, uint16_t field_idx, uint32_t default_val, uint32_t *out_val) {
    size_t voff_entry = 4 + field_idx * sizeof(zc_voffset_t);
    if (voff_entry + sizeof(zc_voffset_t) > reader->vtable_size) {
        *out_val = default_val;
        return true;
    }

    zc_voffset_t field_offset = read_u16(reader->vtable + voff_entry);
    if (field_offset == 0) {
        *out_val = default_val;
        return true;
    }

    if (field_offset + sizeof(uint32_t) > reader->table_size) {
        return false; /* Порушення меж таблиці */
    }

    *out_val = read_u32(reader->root_table + field_offset);
    return true;
}

/* Отримання текстового поля */
bool zc_get_string(const zc_reader_t *reader, uint16_t field_idx, const char **out_str, size_t *out_len) {
    size_t voff_entry = 4 + field_idx * sizeof(zc_voffset_t);
    if (voff_entry + sizeof(zc_voffset_t) > reader->vtable_size) {
        *out_str = "";
        *out_len = 0;
        return true;
    }

    zc_voffset_t field_offset = read_u16(reader->vtable + voff_entry);
    if (field_offset == 0) {
        *out_str = "";
        *out_len = 0;
        return true;
    }

    if (field_offset + sizeof(zc_uoffset_t) > reader->table_size) {
        return false;
    }

    /* Відносний зсув від поля таблиці до початку рядка */
    const uint8_t *ptr_pos = reader->root_table + field_offset;
    zc_uoffset_t rel_offset = read_u32(ptr_pos);
    const uint8_t *str_pos = ptr_pos + rel_offset;

    if (str_pos < reader->buffer || str_pos + sizeof(uint32_t) > reader->buffer + reader->size) {
        return false;
    }

    uint32_t str_len = read_u32(str_pos);
    const uint8_t *str_data = str_pos + sizeof(uint32_t);

    if (str_data + str_len >= reader->buffer + reader->size) {
        return false;
    }

    *out_str = (const char *)str_data;
    *out_len = (size_t)str_len;
    return true;
}

/* Демонстрація створення буфера та прямого доступу */
int main(void) {
    uint8_t buffer[256];
    memset(buffer, 0, sizeof(buffer));

    /* 1. Будуємо рядок "Order-A1" на зміщенні 80 */
    uint8_t *str_ptr = buffer + 80;
    const char *sample_name = "Order-A1";
    uint32_t sample_len = (uint32_t)strlen(sample_name);
    memcpy(str_ptr, &sample_len, 4);
    memcpy(str_ptr + 4, sample_name, sample_len + 1);

    /* 2. Будуємо Vtable на зміщенні 4 */
    /* vtable_size = 10, table_size = 16 */
    /* field #0 (id) -> зсув 4 */
    /* field #1 (price) -> зсув 8 */
    /* field #2 (name) -> зсув 12 */
    uint16_t vtable[] = { 10, 16, 4, 8, 12 };
    memcpy(buffer + 4, vtable, sizeof(vtable));

    /* 3. Будуємо таблицю даних на зміщенні 24 */
    int32_t soffset_vtable = 24 - 4; /* 20 */
    uint32_t field_id = 42001;
    uint32_t field_price = 1999;
    zc_uoffset_t rel_str_offset = (uint32_t)((buffer + 80) - (buffer + 24 + 12));

    memcpy(buffer + 24, &soffset_vtable, 4);
    memcpy(buffer + 28, &field_id, 4);
    memcpy(buffer + 32, &field_price, 4);
    memcpy(buffer + 36, &rel_str_offset, 4);

    /* 4. Записуємо Root Offset = 24 у початок буфера */
    uint32_t root_off = 24;
    memcpy(buffer, &root_off, 4);

    /* 5. Читаємо повідомлення за 0 наносекунд без копіювання */
    zc_reader_t reader;
    if (!zc_reader_init(&reader, buffer, sizeof(buffer))) {
        printf("Помилка валідації буфера!\n");
        return 1;
    }

    uint32_t order_id = 0, price = 0;
    const char *name = NULL;
    size_t name_len = 0;

    zc_get_uint32(&reader, 0, 0, &order_id);
    zc_get_uint32(&reader, 1, 0, &price);
    zc_get_string(&reader, 2, &name, &name_len);

    printf("ID: %u, Ціна: %u, Назва: %.*s\n", order_id, price, (int)name_len, name);
    return 0;
}
