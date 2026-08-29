/* sf_lock.h — взаємне виключення довкола стану черги.
 *
 * push() приходить із високопріоритетного завдання збору даних (а то й
 * прямо з переривання таймера), а peek_tail()/drain/commit_ack — із
 * низькопріоритетного мережевого. Вони діляться покажчиками голови й
 * хвоста ТА єдиним робочим буфером кадру всередині sf_queue_t. Без
 * замка мережеве завдання рано чи пізно прочитає кадр, який збирач
 * саме дописує поверх нього.
 *
 * Черга не знає, що саме дає взаємне виключення: м'ютекс RTOS, заборона
 * переривань чи нічого (однопотоковий вузол). Порожні покажчики —
 * законний випадок і коштують одне порівняння.
 */
#ifndef SF_LOCK_H
#define SF_LOCK_H

typedef struct {
    void (*enter)(void *ctx);
    void (*exit)(void *ctx);
    void *ctx;
} sf_lock_t;

static inline void sf_lock_enter(const sf_lock_t *lock)
{
    if (lock->enter != 0) {
        lock->enter(lock->ctx);
    }
}

static inline void sf_lock_exit(const sf_lock_t *lock)
{
    if (lock->exit != 0) {
        lock->exit(lock->ctx);
    }
}

#endif /* SF_LOCK_H */
