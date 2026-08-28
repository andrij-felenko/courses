#include <stdint.h>
#include <stdbool.h>

#define PAGE_SIZE 4096
#define PAGE_FLAG_LEAF     0x01
#define PAGE_FLAG_ROOT     0x02
#define PAGE_FLAG_OVERFLOW 0x04

#pragma pack(push, 1)

/* Заголовок сторінки B-дерева (24 байти) */
typedef struct PageHeader {
    uint64_t lsn;                 /* WAL Log Sequence Number */
    uint32_t page_id;             /* Номер сторінки в файлі */
    uint16_t flags;               /* Прапорці сторінки */
    uint16_t num_cells;           /* Кількість елементів */
    uint16_t free_space_offset;   /* Верхня межа слотів */
    uint16_t cells_start_offset;  /* Нижня межа комірок даних */
    uint32_t right_sibling_id;    /* Вказівник на праву сусідню сторінку */
} PageHeader;

/* Покажчик комірки (2 байти) */
typedef uint16_t CellOffset;

/* Структура комірки внутрішнього вузла */
typedef struct InternalCell {
    uint32_t child_page_id;       /* Вказівник на дочірній блок */
    uint16_t key_len;             /* Довжина ключа у байтах */
    uint8_t  key_data[];          /* Гнучкий масив даних ключа */
} InternalCell;

/* Структура комірки листка */
typedef struct LeafCell {
    uint16_t key_len;             /* Довжина ключа у байтах */
    uint16_t val_len;             /* Довжина значення/payload у байтах */
    uint8_t  payload[];           /* Спочатку ключ, потім значення */
} LeafCell;

#pragma pack(pop)
