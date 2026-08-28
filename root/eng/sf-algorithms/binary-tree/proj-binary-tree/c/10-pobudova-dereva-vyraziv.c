// Перевірка, чи є символ оператором
bool is_operator(char c) {
    return c == '+' || c == '-' || c == '*' || c == '/';
}

// Побудова дерева виразів з постфіксного рядка на C
Node* build_expression_tree(const char* postfix) {
    Node* stack[100];
    int top = -1;

    for (int i = 0; postfix[i] != '\0'; ++i) {
        char symbol = postfix[i];
        if (symbol == ' ') continue;

        Node* node = create_node(symbol);

        if (is_operator(symbol)) {
            // Дістаємо правий і лівий операнди
            node->right = stack[top--];
            node->left = stack[top--];
        }
        stack[++top] = node;
    }
    return stack[top];
}
