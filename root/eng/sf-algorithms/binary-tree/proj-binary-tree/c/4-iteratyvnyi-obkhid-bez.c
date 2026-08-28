// Ітеративний серединний обхід (In-order) на власному стеку C
void inorder_iterative(Node* root) {
    Node* stack[1000];
    int top = -1;
    Node* current = root;

    while (current != NULL || top >= 0) {
        // Спускаємось до найлівішого вузла, зберігаючи предків у стеку
        while (current != NULL) {
            stack[++top] = current;
            current = current->left;
        }

        // Дістаємо вузол зі стека та обробляємо його
        current = stack[top--];
        printf("%d ", current->data);

        // Переходимо до правого піддерева
        current = current->right;
    }
}
