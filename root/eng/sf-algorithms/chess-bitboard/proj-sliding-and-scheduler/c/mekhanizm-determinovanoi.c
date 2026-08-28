#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <assert.h>

#define MAX_PRIORITIES 64

/* Двозв'язний вузол задачі в системній черзі */
typedef struct TaskNode {
    struct TaskNode *prev;
    struct TaskNode *next;
    uint32_t task_id;
    uint8_t priority;
} TaskNode;

/* Голова черги для кожного пріоритету */
typedef struct {
    TaskNode *head;
    TaskNode *tail;
} PriorityQueue;

/* Планувальник на основі бітової маски */
typedef struct {
    uint64_t active_mask;                 /* Бітова черга: 1 = у черзі є готові потоки */
    PriorityQueue queues[MAX_PRIORITIES]; /* Масив голів черг */
} O1Scheduler;

void scheduler_init(O1Scheduler *sched) {
    sched->active_mask = 0;
    for (int i = 0; i < MAX_PRIORITIES; ++i) {
        sched->queues[i].head = NULL;
        sched->queues[i].tail = NULL;
    }
}

/* Додавання задачі в чергу готовності за O(1) */
void scheduler_enqueue(O1Scheduler *sched, TaskNode *task) {
    uint8_t prio = task->priority;
    assert(prio < MAX_PRIORITIES);

    PriorityQueue *q = &sched->queues[prio];
    task->next = NULL;
    task->prev = q->tail;

    if (q->tail != NULL) {
        q->tail->next = task;
    } else {
        q->head = task;
    }
    q->tail = task;

    /* Встановлюємо біт пріоритету в масці */
    sched->active_mask |= (1ULL << prio);
}

/* Вилучення найпріоритетнішої задачі за O(1) */
TaskNode* scheduler_dequeue_highest(O1Scheduler *sched) {
    if (sched->active_mask == 0) {
        return NULL; /* Немає готових задач (стан Idle) */
    }

    /* Апаратний пошук молодшого встановленого біта (найвищий пріоритет) */
    #if defined(_MSC_VER)
    unsigned long highest_prio;
    _BitScanForward64(&highest_prio, sched->active_mask);
    #else
    int highest_prio = __builtin_ctzll(sched->active_mask);
    #endif

    PriorityQueue *q = &sched->queues[highest_prio];
    TaskNode *task = q->head;
    assert(task != NULL);

    q->head = task->next;
    if (q->head != NULL) {
        q->head->prev = NULL;
    } else {
        q->tail = NULL;
        /* Якщо черга цього рівня спорожніла, скидаємо біт у масці за 1 такт */
        sched->active_mask &= ~(1ULL << highest_prio);
    }

    task->prev = NULL;
    task->next = NULL;
    return task;
}
