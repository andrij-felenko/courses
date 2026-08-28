static void fib_decrease_key(FibHeap *h, Node *x, int newkey) {
    if (newkey > x->key) return;        // тільки зменшення
    x->key = newkey;
    Node *y = x->parent;
    if (y != NULL && x->key < y->key) { // порядок порушено — ріжемо
        fib_cut(h, x, y);
        fib_cascading_cut(h, y);
    }
    if (x->key < h->min->key) h->min = x;
}
