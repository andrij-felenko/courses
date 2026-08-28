#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct Node {
    int id;
    int depth;
    int branch_factor;
    bool is_infinite_path;
} Node;

typedef struct QueueItem {
    Node node;
    struct QueueItem* next;
} QueueItem;

typedef struct {
    QueueItem* head;
    QueueItem* tail;
    size_t size;
} Queue;

Queue* create_queue(void) {
    Queue* q = (Queue*)malloc(sizeof(Queue));
    if (!q) return NULL;
    q->head = q->tail = NULL;
    q->size = 0;
    return q;
}

void enqueue(Queue* q, Node node) {
    QueueItem* item = (QueueItem*)malloc(sizeof(QueueItem));
    if (!item) return;
    item->node = node;
    item->next = NULL;
    if (q->tail) {
        q->tail->next = item;
        q->tail = item;
    } else {
        q->head = q->tail = item;
    }
    q->size++;
}

bool dequeue(Queue* q, Node* out_node) {
    if (!q->head) return false;
    QueueItem* temp = q->head;
    *out_node = temp->node;
    q->head = q->head->next;
    if (!q->head) q->tail = NULL;
    free(temp);
    q->size--;
    return true;
}

void free_queue(Queue* q) {
    Node dummy;
    while (dequeue(q, &dummy));
    free(q);
}

int expand_node(Node parent, Node out_children[2]) {
    if (parent.is_infinite_path) {
        out_children[0] = (Node){ parent.id * 2, parent.depth + 1, 2, true };
        out_children[1] = (Node){ parent.id * 2 + 1, parent.depth + 1, 0, false };
        return 2;
    } else {
        if (parent.depth % 3 == 0) return 0;
        out_children[0] = (Node){ parent.id * 2, parent.depth + 1, 1, false };
        return 1;
    }
}

bool is_target_node(Node node) {
    return (node.depth == 3 && !node.is_infinite_path);
}

bool search_bfs(Node root, int max_visited) {
    Queue* q = create_queue();
    if (!q) return false;

    enqueue(q, root);
    int visited = 0;
    bool found = false;

    printf("[BFS C] Запуск обходу в ширину (сканування рівнів)...\n");
    while (q->size > 0 && visited < max_visited) {
        Node current;
        dequeue(q, &current);
        visited++;

        if (is_target_node(current)) {
            printf("[BFS C] УСПІХ! Ціль знайдено на глибині %d після перевірки %d вузлів.\n", 
                   current.depth, visited);
            found = true;
            break;
        }

        Node children[2];
        int count = expand_node(current, children);
        for (int i = 0; i < count; i++) {
            enqueue(q, children[i]);
        }
    }

    if (!found) {
        printf("[BFS C] Ціль не знайдено за %d перевірених вузлів.\n", visited);
    }
    free_queue(q);
    return found;
}

bool search_dfs(Node current, int* visited, int max_visited) {
    (*visited)++;
    if (*visited >= max_visited) return false;

    if (is_target_node(current)) {
        printf("[DFS C] УСПІХ! Ціль знайдено на глибині %d! Оброблено вузлів: %d\n", 
               current.depth, *visited);
        return true;
    }

    Node children[2];
    int count = expand_node(current, children);
    
    for (int i = 0; i < count; i++) {
        if (search_dfs(children[i], visited, max_visited)) {
            return true;
        }
    }
    return false;
}

int main(void) {
    Node root = { 1, 0, 2, true };

    printf("=== ДЕМОНСТРАЦІЯ ЛЕМИ КЕНІҐА ТА АЛГОРИТМІВ ПОШУКУ (C99) ===\n\n");

    search_bfs(root, 1000);

    int dfs_visited = 0;
    printf("\n[DFS C] Запуск обходу в глибину (ліва гілка є нескінченною)...\n");
    if (!search_dfs(root, &dfs_visited, 100)) {
        printf("[DFS C] ПОМИЛКА: Алгоритм застряг у нескінченній гілці! Перевищено ліміт: %d вузлів.\n", 
               dfs_visited);
    }

    return 0;
}
