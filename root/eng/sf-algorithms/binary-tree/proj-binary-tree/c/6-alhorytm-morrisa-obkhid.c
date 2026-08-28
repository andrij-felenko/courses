// Обхід Морріса (Morris In-order Traversal) мовою C: O(n) час, O(1) пам'ять
void morris_inorder(Node* root) {
    Node* current = root;

    while (current != NULL) {
        if (current->left == NULL) {
            // Якщо немає лівого піддерева — обробляємо вузол і йдемо праворуч
            printf("%d ", current->data);
            current = current->right;
        } else {
            // Знаходимо попередника в серединному обході (найправіший вузол лівого піддерева)
            Node* predecessor = current->left;
            while (predecessor->right != NULL && predecessor->right != current) {
                predecessor = predecessor->right;
            }

            if (predecessor->right == NULL) {
                // Створюємо тимчасове посилання (місток) на поточний вузол
                predecessor->right = current;
                current = current->left;
            } else {
                // Місток уже існує — відновлюємо дерево та обробляємо вузол
                predecessor->right = NULL;
                printf("%d ", current->data);
                current = current->right;
            }
        }
    }
}
