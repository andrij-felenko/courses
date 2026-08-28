/* dlist.c — Виробнича реалізація двохзв'язаного списка з вартовим мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct Node {
    int data;
    struct Node* prev;
    struct Node* next;
} Node;

typedef struct {
    Node sentinel; /* Фіктивний вузол-вартовий */
    size_t size;
} DoublyLinkedList;

/* Ініціалізація порожнього списка */
void dlist_init(DoublyLinkedList* list) {
    list->sentinel.next = &list->sentinel;
    list->sentinel.prev = &list->sentinel;
    list->size = 0;
}

/* Перевірка на порожнечу */
bool dlist_is_empty(const DoublyLinkedList* list) {
    return list->sentinel.next == &list->sentinel;
}

/* Вставка нового вузла між двома наявними вузлами prev_node та next_node */
static void dlist_insert_between(Node* new_node, Node* prev_node, Node* next_node) {
    new_node->prev = prev_node;
    new_node->next = next_node;
    prev_node->next = new_node;
    next_node->prev = new_node;
}

/* Видалення вузла з відв'язуванням покажчиків */
static void dlist_unlink(Node* node) {
    node->prev->next = node->next;
    node->next->prev = node->prev;
}

/* Додавання елемента в кінець списка — O(1) */
bool dlist_push_back(DoublyLinkedList* list, int value) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) return false;
    
    new_node->data = value;
    /* Вставляємо між останнім вузлом (sentinel.prev) та вартовим (sentinel) */
    dlist_insert_between(new_node, list->sentinel.prev, &list->sentinel);
    list->size++;
    return true;
}

/* Додавання елемента на початок списка — O(1) */
bool dlist_push_front(DoublyLinkedList* list, int value) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) return false;
    
    new_node->data = value;
    /* Вставляємо між вартовим (sentinel) та першим вузлом (sentinel.next) */
    dlist_insert_between(new_node, &list->sentinel, list->sentinel.next);
    list->size++;
    return true;
}

/* Видалення вузла з голови списка — O(1) */
bool dlist_pop_front(DoublyLinkedList* list, int* out_value) {
    if (dlist_is_empty(list)) return false;
    
    Node* first = list->sentinel.next;
    if (out_value) *out_value = first->data;
    
    dlist_unlink(first);
    free(first);
    list->size--;
    return true;
}

/* Звільнення всієї пам'яті списка */
void dlist_destroy(DoublyLinkedList* list) {
    Node* current = list->sentinel.next;
    while (current != &list->sentinel) {
        Node* next_node = current->next;
        free(current);
        current = next_node;
    }
    dlist_init(list);
}

int main(void) {
    DoublyLinkedList list;
    dlist_init(&list);

    dlist_push_back(&list, 10);
    dlist_push_back(&list, 20);
    dlist_push_front(&list, 5);

    printf("Розмір списка: %zu\n", list.size);

    int val;
    while (dlist_pop_front(&list, &val)) {
        printf("Вилучено елемент: %d\n", val);
    }

    dlist_destroy(&list);
    return 0;
}
