#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <inttypes.h>

#define WHEEL_L0_BITS  8
#define WHEEL_L0_SIZE  (1U << WHEEL_L0_BITS)
#define WHEEL_L0_MASK  (WHEEL_L0_SIZE - 1)

#define WHEEL_LVL_BITS 6
#define WHEEL_LVL_SIZE (1U << WHEEL_LVL_BITS)
#define WHEEL_LVL_MASK (WHEEL_LVL_SIZE - 1)

#define WHEEL_NUM_LEVELS 4

#define L0_SHIFT 0
#define L1_SHIFT (WHEEL_L0_BITS)
#define L2_SHIFT (WHEEL_L0_BITS + WHEEL_LVL_BITS)
#define L3_SHIFT (WHEEL_L0_BITS + 2 * WHEEL_LVL_BITS)

typedef struct timer_node timer_node_t;
typedef void (*timer_callback_fn)(timer_node_t *node, void *user_data);

struct timer_node {
    uint64_t expires_tick;      /* Абсолютний дедлайн у монотонних тіках */
    uint64_t interval_ticks;    /* Інтервал для періодичних задач (0 для разових) */
    timer_callback_fn callback; /* Покажчик на функцію обробника */
    void *user_data;            /* Контекст користувача */
    timer_node_t *next;         /* Зв'язок вперед для інструзивного списку */
    timer_node_t *prev;         /* Зв'язок назад для O(1) видалення */
    int current_wheel;          /* Індекс колеса: 0..3 або -1 якщо неактивний */
    int current_slot;           /* Індекс слота всередині поточного колеса */
    bool is_active;             /* Прапорець активності вузла */
};

typedef struct {
    timer_node_t *head;
} timer_slot_t;

typedef struct {
    uint64_t current_tick;      /* Поточний монотонний тік (1 тік = 1 мілісекунда) */
    uint64_t base_monotonic_ns; /* Базовий час старту CLOCK_MONOTONIC_RAW */

    /* 4 рівні коліс */
    timer_slot_t l0[WHEEL_L0_SIZE];
    timer_slot_t l1[WHEEL_LVL_SIZE];
    timer_slot_t l2[WHEEL_LVL_SIZE];
    timer_slot_t l3[WHEEL_LVL_SIZE];

    /* Бітові маски зайнятості для прискорення обходу */
    uint64_t l0_mask[WHEEL_L0_SIZE / 64];
    uint64_t l1_mask;
    uint64_t l2_mask;
    uint64_t l3_mask;

    /* Параметри та стан фільтра дрейфу годинника */
    double drift_ppm;
    double phase_error_ms;
    double pi_integral;
    double kp;
    double ki;
} timer_wheel_t;

/* Отримання поточного наносекундного часу через сирий монотонний годинник */
static inline uint64_t timer_get_monotonic_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* Бітові маніпуляції над масками */
static inline void set_bit_l0(uint64_t mask[4], int slot) {
    mask[slot / 64] |= (1ULL << (slot % 64));
}

static inline void clear_bit_l0(uint64_t mask[4], int slot) {
    mask[slot / 64] &= ~(1ULL << (slot % 64));
}

/* Ініціалізація структури таймерного колеса */
void timer_wheel_init(timer_wheel_t *tw) {
    memset(tw, 0, sizeof(*tw));
    tw->base_monotonic_ns = timer_get_monotonic_ns();
    tw->current_tick = 0;
    tw->kp = 0.05;
    tw->ki = 0.001;
    tw->drift_ppm = 0.0;
    tw->phase_error_ms = 0.0;
    tw->pi_integral = 0.0;
}

/* Вставка вузла в початок двозв'язного списку слота */
static void list_insert_node(timer_slot_t *slot, timer_node_t *node) {
    node->next = slot->head;
    node->prev = NULL;
    if (slot->head != NULL) {
        slot->head->prev = node;
    }
    slot->head = node;
}

/* Вилучення вузла з двозв'язного списку слота за O(1) */
static void list_remove_node(timer_slot_t *slot, timer_node_t *node) {
    if (node->prev != NULL) {
        node->prev->next = node->next;
    } else {
        slot->head = node->next;
    }
    if (node->next != NULL) {
        node->next->prev = node->prev;
    }
    node->next = NULL;
    node->prev = NULL;
}

/* Внутрішній розподіл вузла за рівнями */
static void internal_add_timer(timer_wheel_t *tw, timer_node_t *node) {
    uint64_t expires = node->expires_tick;
    uint64_t current = tw->current_tick;

    if (expires <= current) {
        int slot = (int)(current & WHEEL_L0_MASK);
        list_insert_node(&tw->l0[slot], node);
        set_bit_l0(tw->l0_mask, slot);
        node->current_wheel = 0;
        node->current_slot = slot;
        node->is_active = true;
        return;
    }

    uint64_t delta = expires - current;

    if (delta < (1ULL << L1_SHIFT)) {
        int slot = (int)(expires & WHEEL_L0_MASK);
        list_insert_node(&tw->l0[slot], node);
        set_bit_l0(tw->l0_mask, slot);
        node->current_wheel = 0;
        node->current_slot = slot;
    } else if (delta < (1ULL << L2_SHIFT)) {
        int slot = (int)((expires >> L1_SHIFT) & WHEEL_LVL_MASK);
        list_insert_node(&tw->l1[slot], node);
        tw->l1_mask |= (1ULL << slot);
        node->current_wheel = 1;
        node->current_slot = slot;
    } else if (delta < (1ULL << L3_SHIFT)) {
        int slot = (int)((expires >> L2_SHIFT) & WHEEL_LVL_MASK);
        list_insert_node(&tw->l2[slot], node);
        tw->l2_mask |= (1ULL << slot);
        node->current_wheel = 2;
        node->current_slot = slot;
    } else {
        int slot = (int)((expires >> L3_SHIFT) & WHEEL_LVL_MASK);
        list_insert_node(&tw->l3[slot], node);
        tw->l3_mask |= (1ULL << slot);
        node->current_wheel = 3;
        node->current_slot = slot;
    }
    node->is_active = true;
}

/* Публічний інтерфейс реєстрації таймера */
void timer_scheduler_add(timer_wheel_t *tw, timer_node_t *node, 
                         uint64_t delay_ms, uint64_t interval_ms,
                         timer_callback_fn callback, void *user_data) {
    if (node == NULL || callback == NULL) return;
    
    node->expires_tick = tw->current_tick + delay_ms;
    node->interval_ticks = interval_ms;
    node->callback = callback;
    node->user_data = user_data;
    node->next = NULL;
    node->prev = NULL;
    node->current_wheel = -1;
    node->current_slot = -1;

    internal_add_timer(tw, node);
}

/* Публічний інтерфейс скасування таймера за O(1) */
void timer_scheduler_cancel(timer_wheel_t *tw, timer_node_t *node) {
    if (node == NULL || !node->is_active || node->current_wheel < 0) {
        return;
    }

    int wheel = node->current_wheel;
    int slot = node->current_slot;

    if (wheel == 0) {
        list_remove_node(&tw->l0[slot], node);
        if (tw->l0[slot].head == NULL) {
            clear_bit_l0(tw->l0_mask, slot);
        }
    } else if (wheel == 1) {
        list_remove_node(&tw->l1[slot], node);
        if (tw->l1[slot].head == NULL) {
            tw->l1_mask &= ~(1ULL << slot);
        }
    } else if (wheel == 2) {
        list_remove_node(&tw->l2[slot], node);
        if (tw->l2[slot].head == NULL) {
            tw->l2_mask &= ~(1ULL << slot);
        }
    } else if (wheel == 3) {
        list_remove_node(&tw->l3[slot], node);
        if (tw->l3[slot].head == NULL) {
            tw->l3_mask &= ~(1ULL << slot);
        }
    }

    node->is_active = false;
    node->current_wheel = -1;
    node->current_slot = -1;
}

/* Каскадування таймерів з вищого колеса на молодші рівні */
static void cascade_wheel(timer_wheel_t *tw, int wheel_idx, int slot_idx) {
    timer_slot_t *slot = NULL;

    if (wheel_idx == 1) {
        slot = &tw->l1[slot_idx];
        tw->l1_mask &= ~(1ULL << slot_idx);
    } else if (wheel_idx == 2) {
        slot = &tw->l2[slot_idx];
        tw->l2_mask &= ~(1ULL << slot_idx);
    } else if (wheel_idx == 3) {
        slot = &tw->l3[slot_idx];
        tw->l3_mask &= ~(1ULL << slot_idx);
    }

    if (slot == NULL || slot->head == NULL) return;

    timer_node_t *curr = slot->head;
    slot->head = NULL;

    while (curr != NULL) {
        timer_node_t *next = curr->next;
        curr->next = NULL;
        curr->prev = NULL;
        curr->is_active = false;
        curr->current_wheel = -1;
        curr->current_slot = -1;

        internal_add_timer(tw, curr);
        curr = next;
    }
}

/* Просування часу диспетчера вперед до цільового тіка */
void timer_scheduler_advance_to(timer_wheel_t *tw, uint64_t target_tick) {
    while (tw->current_tick < target_tick) {
        uint64_t tick = tw->current_tick;
        int l0_slot = (int)(tick & WHEEL_L0_MASK);

        /* Якщо рівень L0 зробив повний оберт, запускаємо каскад */
        if (l0_slot == 0 && tick > 0) {
            int l1_slot = (int)((tick >> L1_SHIFT) & WHEEL_LVL_MASK);
            cascade_wheel(tw, 1, l1_slot);

            if (l1_slot == 0) {
                int l2_slot = (int)((tick >> L2_SHIFT) & WHEEL_LVL_MASK);
                cascade_wheel(tw, 2, l2_slot);

                if (l2_slot == 0) {
                    int l3_slot = (int)((tick >> L3_SHIFT) & WHEEL_LVL_MASK);
                    cascade_wheel(tw, 3, l3_slot);
                }
            }
        }

        /* Вилучення списку задач поточного мілісекундного слота */
        timer_node_t *expired_list = tw->l0[l0_slot].head;
        tw->l0[l0_slot].head = NULL;
        clear_bit_l0(tw->l0_mask, l0_slot);

        /* Виконання обробників усіх дозрілих таймерів */
        timer_node_t *curr = expired_list;
        while (curr != NULL) {
            timer_node_t *next = curr->next;
            curr->is_active = false;
            curr->current_wheel = -1;
            curr->current_slot = -1;
            curr->next = NULL;
            curr->prev = NULL;

            curr->callback(curr, curr->user_data);

            if (curr->interval_ticks > 0) {
                curr->expires_tick = tick + curr->interval_ticks;
                internal_add_timer(tw, curr);
            }

            curr = next;
        }

        tw->current_tick++;
    }
}

/* Періодичне опитування реального часу */
void timer_scheduler_poll(timer_wheel_t *tw) {
    uint64_t now_ns = timer_get_monotonic_ns();
    uint64_t elapsed_ns = now_ns - tw->base_monotonic_ns;
    uint64_t target_tick = elapsed_ns / 1000000ULL;

    if (target_tick > tw->current_tick) {
        timer_scheduler_advance_to(tw, target_tick);
    }
}
