#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Вузол списку: містить корисне навантаження та зв'язки
typedef struct Node {
    int value;
    struct Node* prev;
    struct Node* next;
} Node;

// Структура списку: тримає фіктивний вартовий вузол прямо за значенням
typedef struct List {
    Node sentinel;
    size_t size;
} List;

// Ініціалізація: вартовий вузол замикається сам на себе
void list_init(List* list) {
    list->sentinel.next = &list->sentinel;
    list->sentinel.prev = &list->sentinel;
    list->sentinel.value = 0; // Значення вартового ніколи не читається
    list->size = 0;
}

// Універсальна вставка НОВОГО вузла ПЕРЕД вказаним вузлом pos.
// Завдяки вартовому працює однаково для вставки на початок, в кінець чи всередину!
void list_insert_before(List* list, Node* pos, int value) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) return;

    new_node->value = value;
    new_node->next = pos;
    new_node->prev = pos->prev;

    pos->prev->next = new_node;
    pos->prev = new_node;

    list->size++;
}

void list_push_back(List* list, int value) {
    // Вставка в кінець = вставка перед вартовим вузлом!
    list_insert_before(list, &list->sentinel, value);
}

void list_push_front(List* list, int value) {
    // Вставка на початок = вставка перед першим елементом (sentinel.next)!
    list_insert_before(list, list->sentinel.next, value);
}

// Універсальне видалення вузла: жодного розгалуження if
void list_remove(List* list, Node* node) {
    if (node == &list->sentinel) return; // Захист: не можна видаляти вартового

    node->prev->next = node->next;
    node->next->prev = node->prev;

    free(node);
    list->size--;
}

void list_clear(List* list) {
    Node* curr = list->sentinel.next;
    while (curr != &list->sentinel) {
        Node* next = curr->next;
        free(curr);
        curr = next;
    }
    list_init(list);
}

void list_print(const List* list) {
    printf("List (size=%zu): [ ", list->size);
    for (Node* curr = list->sentinel.next; curr != &list->sentinel; curr = curr->next) {
        printf("%d ", curr->value);
    }
    printf("]\n");
}

int main(void) {
    List l;
    list_init(&l);

    list_push_back(&l, 10);
    list_push_back(&l, 20);
    list_push_front(&l, 5);
    list_print(&l); // [ 5 10 20 ]

    // Видаляємо перший реальний елемент
    list_remove(&l, l.sentinel.next);
    list_print(&l); // [ 10 20 ]

    list_clear(&l);
    return 0;
}
