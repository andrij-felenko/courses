static Node *fib_extract_min(FibHeap *h) {
    Node *z = h->min;
    if (z == NULL) return NULL;

    if (z->child != NULL) {              // піднімаємо дітей z у кореневий список
        Node *c = z->child;
        do { c->parent = NULL; c = c->right; } while (c != z->child);
        list_union(z, z->child);         // ціле дитяче кільце — в кореневе
    }

    if (z->right == z) {                 // z був єдиним коренем (уже без дітей)
        h->min = NULL;
    } else {
        h->min = z->right;               // тимчасово; consolidate виправить
        list_remove(z);
        fib_consolidate(h);
    }
    h->n--;
    return z;
}
