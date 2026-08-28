/* or_set.h / or_set.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_ITEMS 32
#define MAX_DOTS 64
#define STR_LEN 32

typedef struct {
    char actor[STR_LEN];
    uint64_t counter;
} dot_t;

typedef struct {
    char element[STR_LEN];
    dot_t dots[MAX_DOTS];
    size_t dot_count;
} or_item_t;

typedef struct {
    char actor[STR_LEN];
    uint64_t counter;
    or_item_t items[MAX_ITEMS];
    size_t item_count;
    dot_t tombstones[MAX_DOTS * 2];
    size_t tomb_count;
} or_set_t;

void or_init(or_set_t *set, const char *actor) {
    strncpy(set->actor, actor, STR_LEN - 1);
    set->actor[STR_LEN - 1] = '\0';
    set->counter = 0;
    set->item_count = 0;
    set->tomb_count = 0;
}

static bool dot_in_tombstones(const or_set_t *set, const dot_t *d) {
    for (size_t i = 0; i < set->tomb_count; ++i) {
        if (set->tombstones[i].counter == d->counter &&
            strncmp(set->tombstones[i].actor, d->actor, STR_LEN) == 0) {
            return true;
        }
    }
    return false;
}

void or_add(or_set_t *set, const char *elem) {
    dot_t d;
    strncpy(d.actor, set->actor, STR_LEN - 1);
    d.actor[STR_LEN - 1] = '\0';
    d.counter = ++set->counter;

    for (size_t i = 0; i < set->item_count; ++i) {
        if (strncmp(set->items[i].element, elem, STR_LEN) == 0) {
            if (set->items[i].dot_count < MAX_DOTS) {
                set->items[i].dots[set->items[i].dot_count++] = d;
            }
            return;
        }
    }

    if (set->item_count < MAX_ITEMS) {
        strncpy(set->items[set->item_count].element, elem, STR_LEN - 1);
        set->items[set->item_count].element[STR_LEN - 1] = '\0';
        set->items[set->item_count].dots[0] = d;
        set->items[set->item_count].dot_count = 1;
        set->item_count++;
    }
}

void or_remove(or_set_t *set, const char *elem) {
    for (size_t i = 0; i < set->item_count; ++i) {
        if (strncmp(set->items[i].element, elem, STR_LEN) == 0) {
            for (size_t j = 0; j < set->items[i].dot_count; ++j) {
                if (set->tomb_count < MAX_DOTS * 2) {
                    set->tombstones[set->tomb_count++] = set->items[i].dots[j];
                }
            }
            /* Видаляємо елемент зміщенням масиву */
            set->items[i] = set->items[--set->item_count];
            return;
        }
    }
}
