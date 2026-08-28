#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define TV1_BITS 8
#define TV1_SIZE (1 << TV1_BITS) /* 256 слотів */
#define TV1_MASK (TV1_SIZE - 1)

#define TV2_BITS 6
#define TV2_SIZE (1 << TV2_BITS) /* 64 слоти */
#define TV2_MASK (TV2_SIZE - 1)

typedef void (*timer_callback_t)(uint64_t id, void *user_data);

/* Вузол двозв'язаного списку таймерів */
typedef struct timer_node {
    uint64_t id;                  /* Унікальний ідентифікатор події */
    uint64_t expires;             /* Абсолютний час спрацьовування в тіках */
    timer_callback_t callback;    /* Функція зворотного виклику */
    void *user_data;              /* Контекстний вказівник користувача */
    struct timer_node *prev;      /* Вказівник на попередній вузол */
    struct timer_node *next;      /* Вказівник на наступний вузол */
} timer_node_t;

/* Голова двозв'язаного списку слота */
typedef struct {
    timer_node_t *head;
} timer_list_t;

/* Структура ієрархічного таймерного колеса */
typedef struct {
    uint64_t current_tick;
    timer_list_t tv1[TV1_SIZE];
    timer_list_t tv2[TV2_SIZE];
} timer_wheel_t;

/* Допоміжні функції для роботи зі списком */
static void list_init(timer_list_t *list) {
    list->head = NULL;
}

static void list_add(timer_list_t *list, timer_node_t *node) {
    node->next = list->head;
    node->prev = NULL;
    if (list->head != NULL) {
        list->head->prev = node;
    }
    list->head = node;
}

static void list_remove(timer_list_t *list, timer_node_t *node) {
    if (node->prev != NULL) {
        node->prev->next = node->next;
    } else {
        list->head = node->next;
    }
    if (node->next != NULL) {
        node->next->prev = node->prev;
    }
    node->prev = NULL;
    node->next = NULL;
}

/* Ініціалізація колеса таймерів */
void timer_wheel_init(timer_wheel_t *tw) {
    tw->current_tick = 0;
    for (int i = 0; i < TV1_SIZE; i++) {
        list_init(&tw->tv1[i]);
    }
    for (int i = 0; i < TV2_SIZE; i++) {
        list_init(&tw->tv2[i]);
    }
}

/* Додавання таймера */
timer_node_t* timer_wheel_add(timer_wheel_t *tw, uint64_t id, uint64_t delay,
                              timer_callback_t cb, void *user_data) {
    if (cb == NULL) return NULL;

    timer_node_t *node = (timer_node_t*)malloc(sizeof(timer_node_t));
    if (node == NULL) return NULL;

    node->id = id;
    node->expires = tw->current_tick + delay;
    node->callback = cb;
    node->user_data = user_data;
    node->prev = NULL;
    node->next = NULL;

    uint64_t idx = node->expires - tw->current_tick;

    if (idx < TV1_SIZE) {
        /* Розміщення у TV1 */
        uint32_t slot = node->expires & TV1_MASK;
        list_add(&tw->tv1[slot], node);
    } else if (idx < (1ULL << (TV1_BITS + TV2_BITS))) {
        /* Розміщення у TV2 */
        uint32_t slot = (node->expires >> TV1_BITS) & TV2_MASK;
        list_add(&tw->tv2[slot], node);
    } else {
        /* Обмеження діапазону */
        free(node);
        return NULL;
    }

    return node;
}

/* Скасування таймера */
void timer_wheel_cancel(timer_wheel_t *tw, timer_list_t *owner_list, timer_node_t *node) {
    if (node == NULL) return;
    if (owner_list != NULL) {
        list_remove(owner_list, node);
    }
    free(node);
}

/* Перенесення (каскадування) таймерів із TV2 у TV1 */
static void cascade(timer_wheel_t *tw, uint32_t tv2_slot) {
    timer_node_t *curr = tw->tv2[tv2_slot].head;
    tw->tv2[tv2_slot].head = NULL; /* Очищаємо слот TV2 перед перенесенням */

    while (curr != NULL) {
        timer_node_t *next = curr->next;
        curr->prev = NULL;
        curr->next = NULL;

        /* Усі каскадовані елементи тепер гарантовано потрапляють у TV1 */
        uint32_t tv1_slot = curr->expires & TV1_MASK;
        list_add(&tw->tv1[tv1_slot], curr);

        curr = next;
    }
}

/* Обробка одного кроку часу (Tick) */
void timer_wheel_tick(timer_wheel_t *tw) {
    tw->current_tick++;
    uint32_t tv1_slot = tw->current_tick & TV1_MASK;

    /* Перевіряємо, чи повернулося TV1 на 0 (відбувся повний оберт) */
    if (tv1_slot == 0) {
        uint32_t tv2_slot = (tw->current_tick >> TV1_BITS) & TV2_MASK;
        cascade(tw, tv2_slot);
    }

    /* Обробка всіх дозрілих таймерів у поточному слоті TV1 */
    timer_node_t *curr = tw->tv1[tv1_slot].head;
    tw->tv1[tv1_slot].head = NULL;

    while (curr != NULL) {
        timer_node_t *next = curr->next;
        if (curr->callback != NULL) {
            curr->callback(curr->id, curr->user_data);
        }
        free(curr);
        curr = next;
    }
}

/* Приклад використання */
static void on_timer_expired(uint64_t id, void *user_data) {
    printf("[C TICK] Timer ID %lu expired (msg: %s)\n", id, (char*)user_data);
}

int main(void) {
    timer_wheel_t tw;
    timer_wheel_init(&tw);

    printf("--- Додавання таймерів ---\n");
    timer_wheel_add(&tw, 1, 10,  on_timer_expired, "Short delay (10 ticks)");
    timer_wheel_add(&tw, 2, 260, on_timer_expired, "Long delay (260 ticks, cascade required)");

    for (int i = 0; i < 300; i++) {
        timer_wheel_tick(&tw);
    }

    return 0;
}
