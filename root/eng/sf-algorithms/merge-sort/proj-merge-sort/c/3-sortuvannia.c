#include <stdio.h>
#include <stdlib.h>

typedef struct ListNode {
    int val;
    struct ListNode *next;
} ListNode;

/* Пошук середини списку та розрив зв'язку */
static ListNode* split_list(ListNode *head) {
    if (!head || !head->next) {
        return NULL;
    }

    ListNode *slow = head;
    ListNode *fast = head->next;

    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }

    ListNode *mid = slow->next;
    slow->next = NULL; /* Розриваємо список на дві частини */
    return mid;
}

/* Злиття двох впорядкованих списків без виділення вузлів */
static ListNode* merge_lists(ListNode *l1, ListNode *l2) {
    ListNode dummy;
    ListNode *tail = &dummy;
    dummy.next = NULL;

    while (l1 && l2) {
        if (l1->val <= l2->val) {
            tail->next = l1;
            l1 = l1->next;
        } else {
            tail->next = l2;
            l2 = l2->next;
        }
        tail = tail->next;
    }

    tail->next = l1 ? l1 : l2;
    return dummy.next;
}

/* Головна рекурсивна функція сортування списку */
ListNode* sort_list(ListNode *head) {
    if (!head || !head->next) {
        return head;
    }

    ListNode *mid = split_list(head);
    ListNode *left = sort_list(head);
    ListNode *right = sort_list(mid);

    return merge_lists(left, right);
}
