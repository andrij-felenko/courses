/* Структура допоміжного вектора C */
#include <stdint.h>

typedef struct {
    uint64_t a_type; /* Тип запису (константа AT_*) */
    union {
        uint64_t a_val; /* Цілочисельне значення */
        void *a_ptr;    /* Вказівник на пам'ять */
    } a_un;
} Elf64_auxv_t;
