#include <stdio.h>
#include <stdlib.h>

/* Вузли графа з ручним підрахунком посилань */
typedef struct Node Node;
struct Node {
    int value;
    int ref_count;
    Node *neighbor;
};

Node *node_create(int val) {
    Node *n = (Node *)malloc(sizeof(Node));
    if (!n) return NULL;
    n->value = val;
    n->ref_count = 1;
    n->neighbor = NULL;
    return n;
}

void node_release(Node *n) {
    if (!n) return;
    n->ref_count--;
    if (n->ref_count == 0) {
        if (n->neighbor) {
            node_release(n->neighbor);
        }
        printf("[C Node] Звільнено вузол %d\n", n->value);
        free(n);
    }
}

int main(void) {
    Node *a = node_create(1);
    Node *b = node_create(2);

    /* Створення циклічного посилання: A -> B і B -> A */
    a->neighbor = b;
    b->ref_count++;
    b->neighbor = a;
    a->ref_count++;

    /* Спроба звільнення */
    node_release(a);
    node_release(b);
    /* Обидва вузли залишаються з ref_count == 1, пам'ять витекла */
    return 0;
}
