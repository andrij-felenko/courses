#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct {
    uint8_t is_occupied : 1;      /* 1, якщо слот є канонічним для хоча б одного елемента */
    uint8_t is_continuation : 1;  /* 1, якщо елемент продовжує набіг попереднього слота */
    uint8_t is_shifted : 1;       /* 1, якщо елемент зміщено вправо від канонічного слота */
    uint8_t remainder : 5;        /* Залишок хеш-коду (розмір r бітів) */
} QFSlot;

typedef struct {
    QFSlot *table;                /* Масив слотів розміром num_slots */
    size_t q_bits;                /* Кількість бітів частки (q) */
    size_t r_bits;                /* Кількість бітів залишку (r) */
    size_t num_slots;             /* Загальна кількість слотів m = 2^q */
    size_t slot_mask;             /* Бітова маска індексації (num_slots - 1) */
    size_t count;                 /* Поточна кількість збережених елементів (n) */
} QuotientFilter;
