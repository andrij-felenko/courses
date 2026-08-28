#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_COLUMNS 32

typedef enum {
    TYPE_INT32,
    TYPE_FLOAT64
} ColumnType;

typedef struct {
    uint16_t num_columns;
    ColumnType types[MAX_COLUMNS];
} TableSchema;

/* Кортеж: заголовок з бітовою картою та динамічний масив корисних байтів */
typedef struct {
    uint32_t null_bitmap; /* 1 = NOT NULL, 0 = IS NULL */
    uint16_t payload_size;
    uint8_t* payload;
} Tuple;

void tuple_init(Tuple* t) {
    t->null_bitmap = 0;
    t->payload_size = 0;
    t->payload = NULL;
}

void tuple_free(Tuple* t) {
    if (t->payload) {
        free(t->payload);
        t->payload = NULL;
    }
    t->payload_size = 0;
    t->null_bitmap = 0;
}

bool tuple_set_int32(Tuple* t, uint16_t col_idx, int32_t val) {
    if (col_idx >= MAX_COLUMNS) return false;
    
    /* Виділяємо додаткові 4 байти під int32 */
    uint8_t* new_payload = (uint8_t*)realloc(t->payload, t->payload_size + sizeof(int32_t));
    if (!new_payload) return false;
    
    t->payload = new_payload;
    memcpy(t->payload + t->payload_size, &val, sizeof(int32_t));
    t->payload_size += sizeof(int32_t);
    
    /* Встановлюємо біт присутності */
    t->null_bitmap |= (1U << col_idx);
    return true;
}

void tuple_set_null(Tuple* t, uint16_t col_idx) {
    if (col_idx < MAX_COLUMNS) {
        /* Скидаємо біт присутності; корисні дані не виділяються */
        t->null_bitmap &= ~(1U << col_idx);
    }
}

bool tuple_is_null(const Tuple* t, uint16_t col_idx) {
    return !(t->null_bitmap & (1U << col_idx));
}
