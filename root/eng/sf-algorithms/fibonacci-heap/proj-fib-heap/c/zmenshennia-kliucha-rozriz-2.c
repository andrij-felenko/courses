static void fib_cascading_cut(FibHeap *h, Node *y) {
    Node *z = y->parent;
    if (z != NULL) {
        if (!y->mark) {
            y->mark = true;             // перша втрата — лише позначка
        } else {
            fib_cut(h, y, z);           // друга втрата — ріжемо y теж
            fib_cascading_cut(h, z);    // і котимося до батька
        }
    }
}
