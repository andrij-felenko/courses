#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define BUDDY_MIN_ORDER   4   /* 2^4 = 16 байтів — мінімальний квант під вузол списку */
#define BUDDY_MAX_ORDER  16   /* 2^16 = 64 КБ — максимальний розмір тестового пулу */
#define BUDDY_NUM_ORDERS (BUDDY_MAX_ORDER - BUDDY_MIN_ORDER + 1)

/* Інтрузивний двозв'язний вузол, розміщений у перших байтах вільного блока */
typedef struct list_node {
    struct list_node *prev;
    struct list_node *next;
} list_node_t;

/* Дескриптор мінімального кванта для точного контролю статусу та порядку */
typedef struct {
    uint8_t order;      /* дійсний порядок виділеного або вільного блока */
    uint8_t is_free;    /* 1 = у списку вільних, 0 = зайнятий під корисні дані */
} block_tag_t;

/* Головний контекст розподілювача пам'яті */
typedef struct {
    uint8_t *pool;                           /* базовий вказівник на сирий масив пам'яті */
    size_t pool_size;                        /* загальний розмір пулу в байтах (2^MAX_ORDER) */
    list_node_t free_lists[BUDDY_NUM_ORDERS];/* масив голів вільних списків для кожного порядку */
    block_tag_t tags[1 << (BUDDY_MAX_ORDER - BUDDY_MIN_ORDER)]; /* масив тегів квантів */
} buddy_allocator_t;

/* Циклічний двозв'язний список зі сторожовим елементом (Sentinel Node) */
static void list_init(list_node_t *head) {
    head->prev = head;
    head->next = head;
}

static bool list_is_empty(const list_node_t *head) {
    return head->next == head;
}

static void list_push(list_node_t *head, list_node_t *node) {
    node->next = head->next;
    node->prev = head;
    head->next->prev = node;
    head->next = node;
}

static void list_remove(list_node_t *node) {
    node->prev->next = node->next;
    node->next->prev = node->prev;
    node->prev = NULL;
    node->next = NULL;
}

static list_node_t *list_pop(list_node_t *head) {
    if (list_is_empty(head)) return NULL;
    list_node_t *node = head->next;
    list_remove(node);
    return node;
}

/* Переведення розміру байтів у мінімально достатній логарифмічний порядок */
static uint8_t size_to_order(size_t size) {
    uint8_t order = BUDDY_MIN_ORDER;
    size_t block_size = (size_t)1 << BUDDY_MIN_ORDER;
    while (block_size < size && order < BUDDY_MAX_ORDER) {
        order++;
        block_size <<= 1;
    }
    return order;
}

/* Ініціалізація алокатора поверх наданого сирого буфера */
bool buddy_init(buddy_allocator_t *alloc, void *raw_memory, size_t size) {
    if (!alloc || !raw_memory || size < ((size_t)1 << BUDDY_MAX_ORDER)) {
        return false;
    }
    alloc->pool = (uint8_t *)raw_memory;
    alloc->pool_size = (size_t)1 << BUDDY_MAX_ORDER;

    for (int i = 0; i < BUDDY_NUM_ORDERS; i++) {
        list_init(&alloc->free_lists[i]);
    }

    size_t num_tags = (size_t)1 << (BUDDY_MAX_ORDER - BUDDY_MIN_ORDER);
    for (size_t i = 0; i < num_tags; i++) {
        alloc->tags[i].order = 0;
        alloc->tags[i].is_free = 0;
    }

    /* Початковий стан: один монолітний блок максимального порядку вільний */
    list_node_t *root_block = (list_node_t *)alloc->pool;
    uint8_t max_list_idx = BUDDY_MAX_ORDER - BUDDY_MIN_ORDER;
    list_push(&alloc->free_lists[max_list_idx], root_block);

    alloc->tags[0].order = BUDDY_MAX_ORDER;
    alloc->tags[0].is_free = 1;

    return true;
}

/* Виділення пам'яті з рекурсивним розщепленням донорів */
void *buddy_alloc(buddy_allocator_t *alloc, size_t size) {
    if (!alloc || size == 0 || size > alloc->pool_size) {
        return NULL;
    }

    uint8_t target_order = size_to_order(size);
    uint8_t current_order = target_order;

    /* Шукаємо перший непорожній список порядку >= target_order */
    while (current_order <= BUDDY_MAX_ORDER) {
        uint8_t list_idx = current_order - BUDDY_MIN_ORDER;
        if (!list_is_empty(&alloc->free_lists[list_idx])) {
            break;
        }
        current_order++;
    }

    if (current_order > BUDDY_MAX_ORDER) {
        return NULL; /* Пам'ять вичерпана або фрагментована */
    }

    /* Вилучаємо блок-донор зі списку */
    uint8_t found_list_idx = current_order - BUDDY_MIN_ORDER;
    list_node_t *block = list_pop(&alloc->free_lists[found_list_idx]);
    uintptr_t block_offset = (uint8_t *)block - alloc->pool;

    /* Послідовно розщеплюємо донор навпіл, поки не отримаємо цільовий порядок */
    while (current_order > target_order) {
        current_order--;
        uint8_t split_list_idx = current_order - BUDDY_MIN_ORDER;
        size_t half_size = (size_t)1 << current_order;

        /* Правий близнюк отримує зміщення block_offset + half_size */
        uintptr_t buddy_offset = block_offset + half_size;
        list_node_t *buddy = (list_node_t *)(alloc->pool + buddy_offset);

        /* Додаємо правого близнюка у відповідний список вільних */
        list_push(&alloc->free_lists[split_list_idx], buddy);

        size_t buddy_tag_idx = buddy_offset >> BUDDY_MIN_ORDER;
        alloc->tags[buddy_tag_idx].order = current_order;
        alloc->tags[buddy_tag_idx].is_free = 1;
    }

    /* Позначаємо лівий цільовий блок як зайнятий */
    size_t block_tag_idx = block_offset >> BUDDY_MIN_ORDER;
    alloc->tags[block_tag_idx].order = target_order;
    alloc->tags[block_tag_idx].is_free = 0;

    return (void *)block;
}

/* Звільнення пам'яті та каскадне злиття близнюків */
void buddy_free(buddy_allocator_t *alloc, void *ptr) {
    if (!alloc || !ptr) return;

    uint8_t *byte_ptr = (uint8_t *)ptr;
    if (byte_ptr < alloc->pool || byte_ptr >= alloc->pool + alloc->pool_size) {
        return; /* Захист від некоректної адреси поза пулом */
    }

    uintptr_t block_offset = byte_ptr - alloc->pool;
    size_t tag_idx = block_offset >> BUDDY_MIN_ORDER;
    uint8_t order = alloc->tags[tag_idx].order;

    if (alloc->tags[tag_idx].is_free) {
        return; /* Захист від подвійного звільнення (Double Free) */
    }

    /* Каскадне злиття близнюків */
    while (order < BUDDY_MAX_ORDER) {
        /* Обчислюємо зміщення близнюка через XOR */
        uintptr_t buddy_offset = block_offset ^ ((uintptr_t)1 << order);
        size_t buddy_tag_idx = buddy_offset >> BUDDY_MIN_ORDER;

        /* Перевіряємо умови злиття: близнюк вільний і має тотожний порядок */
        if (!alloc->tags[buddy_tag_idx].is_free ||
            alloc->tags[buddy_tag_idx].order != order) {
            break; /* Злиття неможливе: напарник зайнятий або розщеплений */
        }

        /* Вилучаємо близнюка зі списку вільних */
        list_node_t *buddy_node = (list_node_t *)(alloc->pool + buddy_offset);
        list_remove(buddy_node);

        /* Скидаємо метадані поглиненого близнюка */
        alloc->tags[buddy_tag_idx].is_free = 0;
        alloc->tags[buddy_tag_idx].order = 0;

        /* Базовою адресою батьківського блока стає ліва адреса */
        block_offset = block_offset & ~((uintptr_t)1 << order);
        tag_idx = block_offset >> BUDDY_MIN_ORDER;
        order++;
    }

    /* Повертаємо підсумковий укрупнений блок у список вільних */
    uint8_t final_list_idx = order - BUDDY_MIN_ORDER;
    list_node_t *final_block = (list_node_t *)(alloc->pool + block_offset);
    list_push(&alloc->free_lists[final_list_idx], final_block);

    alloc->tags[tag_idx].order = order;
    alloc->tags[tag_idx].is_free = 1;
}
