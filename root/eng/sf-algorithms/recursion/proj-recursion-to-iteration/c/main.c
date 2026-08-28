long tree_sum(Node *root) {
    // власний стек: масив вказівників у КУПІ, а не системний стек викликів
    size_t cap = 64, top = 0;
    Node **stack = malloc(cap * sizeof(Node *));
    stack[top++] = root;

    long total = 0;
    while (top > 0) {                       // поки стек не порожній
        Node *node = stack[--top];          // pop
        total += node->value;
        for (size_t i = 0; i < node->n_children; i++) {
            if (top == cap) {               // стек доріс — подвоюємо, як у Go
                cap *= 2;
                stack = realloc(stack, cap * sizeof(Node *));
            }
            stack[top++] = node->children[i];   // push
        }
    }
    free(stack);
    return total;
}
