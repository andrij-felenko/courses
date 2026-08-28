#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>
#include <math.h>

typedef struct Node {
    int  key;                  // ключ (за ним упорядкування)
    int  degree;               // кількість безпосередніх дітей
    bool mark;                 // чи втратив дитину, відколи став не-коренем
    struct Node *parent;       // батько (NULL у кореня)
    struct Node *child;        // одна з дітей (решта — через її кільце)
    struct Node *left, *right; // сусіди в кільці (кореневому чи дитячому)
} Node;

// Вкинути кільце вузла b одразу після a (обидва — у якихось кільцях).
// Коли b самотній, це просто вставляє b між a та a->right.
static void list_union(Node *a, Node *b) {
    Node *a_next = a->right;
    Node *b_prev = b->left;
    a->right = b;
    b->left  = a;
    b_prev->right = a_next;
    a_next->left  = b_prev;
}

// Вирвати x із його кільця; x лишається замкненим сам на себе.
static void list_remove(Node *x) {
    x->left->right = x->right;
    x->right->left = x->left;
    x->left = x->right = x;    // тепер x — самотнє кільце
}
