// Концептуальна модель черги мікрозадач у C
#include <stdio.h>
#include <stdlib.h>

typedef void (*task_fn)(void *data);

typedef struct task_node {
    task_fn fn;
    void *data;
    struct task_node *next;
} task_node_t;

typedef struct {
    task_node_t *head;
    task_node_t *tail;
} microtask_queue_t;

void enqueue_microtask(microtask_queue_t *q, task_fn fn, void *data) {
    task_node_t *node = malloc(sizeof(task_node_t));
    node->fn = fn;
    node->data = data;
    node->next = NULL;
    if (q->tail) {
        q->tail->next = node;
        q->tail = node;
    } else {
        q->head = q->tail = node;
    }
}

void drain_microtasks(microtask_queue_t *q) {
    while (q->head) {
        task_node_t *node = q->head;
        q->head = node->next;
        if (!q->head) q->tail = NULL;

        node->fn(node->data);
        free(node);
    }
}
