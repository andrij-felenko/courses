/* kernel_list_example.c — Демонстрація інтрузивного списка Linux Kernel */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>

/* Проста емуляція макросів ядра Linux */
struct list_head {
    struct list_head *next, *prev;
};

#define INIT_LIST_HEAD(ptr) do { \
    (ptr)->next = (ptr); (ptr)->prev = (ptr); \
} while (0)

#define container_of(ptr, type, member) \
    ((type *)((char *)(ptr) - offsetof(type, member)))

#define list_entry(ptr, type, member) \
    container_of(ptr, type, member)

#define list_for_each(pos, head) \
    for (pos = (head)->next; pos != (head); pos = pos->next)

/* Прикладна структура процесу, що містить інтрузивний list_head */
typedef struct {
    int pid;
    char name[32];
    struct list_head list_node; /* Вбудований вузол */
} ProcessTask;

static inline void list_add_tail(struct list_head *new_node, struct list_head *head) {
    struct list_head *prev_node = head->prev;
    new_node->next = head;
    new_node->prev = prev_node;
    prev_node->next = new_node;
    head->prev = new_node;
}

int main(void) {
    struct list_head process_list;
    INIT_LIST_HEAD(&process_list);

    /* Створюємо два процеси без додаткового allocation під вузли списка */
    ProcessTask p1 = {.pid = 101, .name = "systemd"};
    ProcessTask p2 = {.pid = 502, .name = "nginx"};

    list_add_tail(&p1.list_node, &process_list);
    list_add_tail(&p2.list_node, &process_list);

    /* Обхід списка за допомогою container_of */
    struct list_head *curr;
    list_for_each(curr, &process_list) {
        ProcessTask *task = list_entry(curr, ProcessTask, list_node);
        printf("Процес PID: %d, Назва: %s\n", task->pid, task->name);
    }

    return 0;
}
