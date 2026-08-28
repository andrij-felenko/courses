// НЕБЕЗПЕЧНО: порядок взяття замків залежить від переданих аргументів!
void swap_nodes_unsafe(node_t *a, node_t *b) {
    pthread_mutex_lock(&a->mtx);
    pthread_mutex_lock(&b->mtx);

    int temp = a->value;
    a->value = b->value;
    b->value = temp;

    pthread_mutex_unlock(&b->mtx);
    pthread_mutex_unlock(&a->mtx);
}
