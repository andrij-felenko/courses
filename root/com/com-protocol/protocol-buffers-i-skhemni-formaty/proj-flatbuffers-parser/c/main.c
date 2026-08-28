#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

// Приклад ручного кодека за специфікацією FlatBuffers Binary Wire Format
typedef struct {
    float x, y, z;
} Vector3;

// Побудова буфера FlatBuffers вручну (пам'ять заповнюється з кінця до початку)
typedef struct {
    uint8_t *buf;
    size_t   capacity;
    size_t   head; // курсор зміщення від початку буфера (росте вниз)
} FlatBuilder;

static void fb_init(FlatBuilder *b, uint8_t *buf, size_t cap) {
    b->buf = buf;
    b->capacity = cap;
    b->head = cap;
}

static uint32_t fb_push_bytes(FlatBuilder *b, const void *data, size_t size, size_t align) {
    // вирівнювання вниз
    size_t new_head = (b->head - size) & ~(align - 1);
    b->head = new_head;
    if (data) memcpy(&b->buf[b->head], data, size);
    return (uint32_t)(b->capacity - b->head); // зміщення від кінця
}

static uint32_t fb_create_string(FlatBuilder *b, const char *str) {
    size_t len = strlen(str);
    // 1 байт нуль-термінатора
    fb_push_bytes(b, "", 1, 1);
    // тіло рядка
    fb_push_bytes(b, str, len, 1);
    // довжина рядка uint32
    uint32_t l = (uint32_t)len;
    return fb_push_bytes(b, &l, 4, 4);
}

// Створення об'єкта SensorReport
static uint32_t fb_build_report(FlatBuilder *b, uint32_t ts, uint32_t id, int32_t temp,
                                uint32_t bat, const Vector3 *accel, const char *name) {
    // 1. Спочатку створюємо непрямі об'єкти (рядки)
    uint32_t name_offset = fb_create_string(b, name);

    // 2. Створюємо vtable (довжина vtable, довжина об'єкта, зсуви полів)
    // Поля: 0:ts (4), 1:id (4), 2:temp (4), 3:bat (4), 4:accel (12), 5:name (4)
    uint16_t vtable[8];
    vtable[0] = 8 * sizeof(uint16_t); // vtable_size = 16 Б
    vtable[1] = 4 + 4 + 4 + 4 + 4 + 12 + 4; // object_size = 36 Б
    vtable[2] = 4;   // offset field 0 (ts)
    vtable[3] = 8;   // offset field 1 (id)
    vtable[4] = 12;  // offset field 2 (temp)
    vtable[5] = (bat == 3300) ? 0 : 16; // 0 якщо дефолт!
    vtable[6] = 20;  // offset field 4 (accel struct)
    vtable[7] = 32;  // offset field 5 (name offset)

    // 3. Записуємо поля об'єкта в Table Data
    size_t table_start = (b->head - 36) & ~3;
    b->head = table_start;
    uint8_t *t = &b->buf[table_start];

    // Зсув до рядка name (відносний від позиції поля t[32])
    uint32_t rel_name = (uint32_t)((b->capacity - name_offset) - (table_start + 32));
    memcpy(&t[4],  &ts, 4);
    memcpy(&t[8],  &id, 4);
    memcpy(&t[12], &temp, 4);
    if (bat != 3300) memcpy(&t[16], &bat, 4);
    if (accel) memcpy(&t[20], accel, 12);
    memcpy(&t[32], &rel_name, 4);

    // 4. Записуємо vtable перед об'єктом і зв'язуємо відносним зсувом
    uint32_t vt_pos = fb_push_bytes(b, vtable, sizeof(vtable), 2);
    int32_t vt_offset = (int32_t)(b->capacity - vt_pos) - (int32_t)table_start;
    memcpy(&t[0], &vt_offset, 4); // перші 4 байти таблиці вказують на vtable

    return (uint32_t)(b->capacity - table_start);
}

// Завершення буфера: запис кореневого зсуву на початку
static size_t fb_finish(FlatBuilder *b, uint32_t root_offset) {
    uint32_t root_pos = (uint32_t)(b->capacity - root_offset);
    uint32_t rel_root = root_pos - (uint32_t)(b->head - 4);
    fb_push_bytes(b, &rel_root, 4, 4);
    return b->capacity - b->head;
}

// Пряме читання полів (Zero-Copy) без декодування
typedef struct {
    const uint8_t *table;
    const uint16_t *vtable;
    uint16_t vtable_size;
} SensorReportReader;

static bool fb_read_report(const uint8_t *buf, size_t len, SensorReportReader *r) {
    if (len < 8) return false;
    uint32_t root_offset;
    memcpy(&root_offset, buf, 4);
    if (root_offset + 4 > len) return false;

    r->table = buf + root_offset;
    int32_t vt_offset;
    memcpy(&vt_offset, r->table, 4);
    
    const uint8_t *vt_ptr = r->table - vt_offset;
    if (vt_ptr < buf || vt_ptr + 4 > buf + len) return false;

    r->vtable = (const uint16_t *)vt_ptr;
    r->vtable_size = r->vtable[0] / sizeof(uint16_t);
    return true;
}

static uint32_t get_timestamp(const SensorReportReader *r) {
    if (r->vtable_size <= 2 || r->vtable[2] == 0) return 0;
    uint32_t val;
    memcpy(&val, r->table + r->vtable[2], 4);
    return val;
}

static uint32_t get_battery(const SensorReportReader *r) {
    // Якщо зміщення 0 у vtable — повертаємо домовлене значення за замовчуванням
    if (r->vtable_size <= 5 || r->vtable[5] == 0) return 3300;
    uint32_t val;
    memcpy(&val, r->table + r->vtable[5], 4);
    return val;
}

static const char *get_name(const SensorReportReader *r) {
    if (r->vtable_size <= 7 || r->vtable[7] == 0) return "";
    uint32_t rel_offset;
    memcpy(&rel_offset, r->table + r->vtable[7], 4);
    const uint8_t *str_ptr = r->table + r->vtable[7] + rel_offset;
    return (const char *)(str_ptr + 4); // пропускаємо 4 байти довжини
}
