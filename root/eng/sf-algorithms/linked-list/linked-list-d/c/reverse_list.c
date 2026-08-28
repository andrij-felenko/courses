/* reverse_list.c — Алгоритм перевертання однозв'язаного списка мовою C */
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* reverse_list(Node* head) {
    Node* prev = NULL;
    Node* curr = head;
    Node* next_node = NULL;

    while (curr != NULL) {
        next_node = curr->next; /* 1. Зберігаємо наступний вузол */
        curr->next = prev;      /* 2. Розвертаємо покажчик назад */
        prev = curr;            /* 3. Зсуваємо prev на поточний */
        curr = next_node;       /* 4. Переходимо до наступного */
    }

    return prev; /* Новий head розвернутого списка */
}
