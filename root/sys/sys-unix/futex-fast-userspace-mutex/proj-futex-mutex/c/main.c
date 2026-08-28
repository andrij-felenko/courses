#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>
#include <time.h>
#include <pthread.h>

// Системна обгортка для операції очікування futex_wait
static inline int futex_wait(atomic_uint *uaddr, unsigned int val) {
    return syscall(SYS_futex, uaddr, FUTEX_WAIT_PRIVATE, val, NULL, NULL, 0);
}

// Системна обгортка для операції пробудження futex_wake
static inline int futex_wake(atomic_uint *uaddr, int count) {
    return syscall(SYS_futex, uaddr, FUTEX_WAKE_PRIVATE, count, NULL, NULL, 0);
}

// Системна обгортка для операції перепідключення futex_cmp_requeue
static inline int futex_cmp_requeue(atomic_uint *uaddr1, atomic_uint *uaddr2,
                                   int wake_count, int requeue_count, unsigned int val3) {
    return syscall(SYS_futex, uaddr1, FUTEX_CMP_REQUEUE_PRIVATE, wake_count,
                   requeue_count, uaddr2, val3);
}

// Структура тристанового м'ютекса
typedef struct {
    atomic_uint state; // 0 = unlocked, 1 = locked without waiters, 2 = locked with waiters
} futex_mutex_t;

void futex_mutex_init(futex_mutex_t *m) {
    atomic_store(&m->state, 0);
}

void futex_mutex_lock(futex_mutex_t *m) {
    unsigned int c = 0;
    // Швидкий шлях: спроба змінити 0 -> 1 у просторі користувача
    if (atomic_compare_exchange_strong(&m->state, &c, 1)) {
        return; // Захоплено швидко без системного виклику
    }

    // Повільний шлях: м'ютекс зайнятий, фіксуємо наявність очікуючих
    if (c != 2) {
        c = atomic_exchange(&m->state, 2);
    }
    
    while (c != 0) {
        // Засинаємо у ядрі, лише якщо стан досі 2
        futex_wait(&m->state, 2);
        c = atomic_exchange(&m->state, 2);
    }
}

void futex_mutex_unlock(futex_mutex_t *m) {
    // Якщо стан був 1, новий стан 0, повертаємося швидко
    if (atomic_fetch_sub(&m->state, 1) != 1) {
        // Були очікуючі потоки (стан був 2)
        atomic_store(&m->state, 0);
        // Будимо 1 очікуючий потік у ядрі
        futex_wake(&m->state, 1);
    }
}

// Структура умовної змінної
typedef struct {
    atomic_uint sequence;
} futex_cond_t;

void futex_cond_init(futex_cond_t *c) {
    atomic_store(&c->sequence, 0);
}

void futex_cond_wait(futex_cond_t *c, futex_mutex_t *m) {
    unsigned int seq = atomic_load(&c->sequence);
    
    // Відпускаємо м'ютекс перед засинанням
    futex_mutex_unlock(m);
    
    // Чекаємо на зміну sequence у ядрі
    futex_wait(&c->sequence, seq);
    
    // Після пробудження знову захоплюємо м'ютекс
    futex_mutex_lock(m);
}

void futex_cond_signal(futex_cond_t *c) {
    atomic_fetch_add(&c->sequence, 1);
    futex_wake(&c->sequence, 1);
}

void futex_cond_broadcast(futex_cond_t *c, futex_mutex_t *m) {
    unsigned int seq = atomic_fetch_add(&c->sequence, 1) + 1;
    // Будимо 1 потік на condvar, а решту (INT_MAX) переносимо в чергу м'ютекса m
    futex_cmp_requeue(&c->sequence, &m->state, 1, 2147483647, seq);
}
