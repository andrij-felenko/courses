#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node *prev, *next;
} Node;

// ЗВИЧАЙНИЙ список: 4 розгалуження для обробки країв
void remove_classic(Node** head, Node** tail, Node* node) {
    if (node->prev != NULL) {
        node->prev->next = node->next;
    } else {
        *head = node->next;
    }
    if (node->next != NULL) {
        node->next->prev = node->prev;
    } else {
        *tail = node->prev;
    }
    free(node);
}

// СПИСОК З ВАРТОВИМ: 0 розгалужень, чисті присвоєння покажчиків
void remove_sentinel(Node* node) {
    node->prev->next = node->next;
    node->next->prev = node->prev;
    free(node);
}
