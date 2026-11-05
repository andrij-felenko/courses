#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct Node {
    int value;
    struct Node* next;
} Node;

// Атомарна зміна вказівника на голову списку за допомогою atomic_compare_exchange_weak
bool try_update_head(Node* volatile* head, Node* old_head, Node* new_head) {
    // Змінна expected має бути модифікованою, оскільки вона передається за вказівником
    Node* expected = old_head;
    
    // Якщо головний вказівник збігається з expected, він замінюється на new_head.
    // У разі невдачі (зокрема через spurious failure) expected оновлюється поточним значенням *head.
    return atomic_compare_exchange_weak(head, &expected, new_head);
}
