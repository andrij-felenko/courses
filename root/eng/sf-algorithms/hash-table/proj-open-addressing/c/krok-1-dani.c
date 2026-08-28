#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>

typedef enum { EMPTY = 0, OCCUPIED, DELETED } State;   // EMPTY=0 → calloc дає порожні

typedef struct {
    char  *key;      // копія тексту ключа в купі; NULL, коли комірка не зайнята
    long   value;    // навантаження; тут — ціле, для прикладу
    State  state;    // EMPTY / OCCUPIED / DELETED (надгробок)
} Slot;

typedef struct {
    Slot  *slots;    // суцільний масив комірок
    size_t cap;      // місткість — ЗАВЖДИ степінь двійки
    size_t len;      // живих записів (OCCUPIED)
    size_t used;     // OCCUPIED + DELETED — скільки комірок «не порожні»
} HashTable;
