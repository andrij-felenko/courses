#include <stdlib.h>

struct ListNode {
    int val;
    struct ListNode *next;
};

/* Сортування однозв'язного списку вставками на C */
struct ListNode* sort_linked_list(struct ListNode *head) {
    if (head == NULL || head->next == NULL) {
        return head;
    }

    /* Фіктивний головний вузол для спрощення вставки на початок списку */
    struct ListNode dummy;
    dummy.val = 0;
    dummy.next = NULL;

    struct ListNode *curr = head;
    while (curr != NULL) {
        struct ListNode *next_node = curr->next;
        
        /* Шукаємо позицію вставки у відсортованому результуючому списку */
        struct ListNode *prev = &dummy;
        while (prev->next != NULL && prev->next->val <= curr->val) {
            prev = prev->next;
        }

        /* Вставляємо поточний вузол між prev та prev->next */
        curr->next = prev->next;
        prev->next = curr;

        curr = next_node;
    }

    return dummy.next;
}
