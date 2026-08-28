// Прошитий вузол двійкового дерева мовою C
typedef struct ThreadedNode {
    int data;
    struct ThreadedNode* left;
    struct ThreadedNode* right;
    bool left_is_thread;   // true, якщо left вказує на попередника
    bool right_is_thread;  // true, якщо right вказує на наступника
} ThreadedNode;

// Знаходження найлівішого вузла в піддереві
ThreadedNode* left_most(ThreadedNode* node) {
    if (node == NULL) return NULL;
    while (!node->left_is_thread && node->left != NULL) {
        node = node->left;
    }
    return node;
}

// Серединний обхід прошитого дерева без стека і без рекурсії за O(n) час та O(1) пам'ять
void threaded_inorder(ThreadedNode* root) {
    ThreadedNode* current = left_most(root);

    while (current != NULL) {
        printf("%d ", current->data);

        if (current->right_is_thread) {
            // Перехід за прошитим нитковим посиланням до наступника
            current = current->right;
        } else {
            // Перехід до найлівішого вузла в правому піддереві
            current = left_most(current->right);
        }
    }
}
