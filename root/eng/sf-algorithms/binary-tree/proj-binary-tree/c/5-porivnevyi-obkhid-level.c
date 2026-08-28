// Черга для вузлів C-версії (спрощена реалізація на масиві)
#define MAX_QUEUE 1000

void print_level_order(Node* root) {
    if (root == NULL) return;

    Node* queue[MAX_QUEUE];
    int head = 0, tail = 0;

    queue[tail++] = root;

    while (head < tail) {
        Node* current = queue[head++];
        printf("%d ", current->data);

        if (current->left != NULL) {
            queue[tail++] = current->left;
        }
        if (current->right != NULL) {
            queue[tail++] = current->right;
        }
    }
}
