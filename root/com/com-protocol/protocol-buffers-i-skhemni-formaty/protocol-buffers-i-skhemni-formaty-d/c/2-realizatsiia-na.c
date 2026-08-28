#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Формування буфера FlatBuffers у C-стилі (спрощена модель генерації)
typedef struct {
    uint8_t *buffer;
    size_t   capacity;
    size_t   head;
} FbBuilder;

static void fb_init(FbBuilder *b, uint8_t *buf, size_t cap) {
    b->buffer = buf;
    b->capacity = cap;
    b->head = cap;
}

static size_t fb_build_reading(FbBuilder *b, uint32_t ts, uint32_t id, int32_t temp, uint32_t bat) {
    // 1. Формування vtable: [vtable_size (2B), object_size (2B), offset0, offset1, offset2, offset3]
    uint16_t vtable[6];
    vtable[0] = 6 * sizeof(uint16_t); // 12 байтів
    vtable[1] = 4 + 4 + 4 + 4 + 4;     // 20 байтів тіла таблиці
    vtable[2] = 4;                     // offset ts
    vtable[3] = 8;                     // offset id
    vtable[4] = 12;                    // offset temp
    vtable[5] = (bat == 3300) ? 0 : 16;// 0 якщо значення за замовчуванням!

    // 2. Виділення місця під Table Data (вирівнювання на 4 байти)
    size_t table_start = (b->head - 20) & ~3;
    b->head = table_start;
    uint8_t *t = &b->buffer[table_start];

    memcpy(&t[4],  &ts, 4);
    memcpy(&t[8],  &id, 4);
    memcpy(&t[12], &temp, 4);
    if (bat != 3300) memcpy(&t[16], &bat, 4);

    // 3. Запис vtable перед Table Data
    size_t vt_start = (b->head - sizeof(vtable)) & ~1;
    b->head = vt_start;
    memcpy(&b->buffer[vt_start], vtable, sizeof(vtable));

    // 4. Зв'язування: Table Data[0] містить від'ємний зсув назад до vtable
    int32_t vt_rel = (int32_t)vt_start - (int32_t)table_start;
    memcpy(&t[0], &vt_rel, 4);

    // 5. Запис кореневого покажчика (перші 4 байти буфера)
    uint32_t root_offset = (uint32_t)table_start;
    size_t root_start = (b->head - 4) & ~3;
    b->head = root_start;
    memcpy(&b->buffer[root_start], &root_offset, 4);

    return b->capacity - b->head;
}

// Пряме читання полів без розбору
static uint32_t fb_get_sensor_id(const uint8_t *buf, size_t len) {
    if (len < 8) return 0;
    uint32_t root_offset;
    memcpy(&root_offset, buf, 4);
    if (root_offset + 4 > len) return 0;

    const uint8_t *table = buf + root_offset;
    int32_t vt_offset;
    memcpy(&vt_offset, table, 4);

    const uint8_t *vtable_ptr = table + vt_offset;
    if (vtable_ptr < buf || vtable_ptr + 8 > buf + len) return 0;

    const uint16_t *vtable = (const uint16_t *)vtable_ptr;
    uint16_t field_off = vtable[3]; // індекс поля 1 (sensor_id)
    if (field_off == 0) return 0;

    uint32_t val;
    memcpy(&val, table + field_off, 4);
    return val;
}
