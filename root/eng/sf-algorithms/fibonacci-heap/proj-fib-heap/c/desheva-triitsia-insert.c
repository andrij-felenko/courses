// Вставити ключ. Повертає вузол — щоб потім можна було decrease/delete.
static Node *fib_insert(FibHeap *h, int key) {
    Node *x = make_node(key);
    if (h->min == NULL) {
        h->min = x;                 // x уже сам собі кореневий список
    } else {
        list_union(h->min, x);      // вкинути в кореневий список
        if (x->key < h->min->key) h->min = x;
    }
    h->n++;
    return x;
}

// Підглянути мінімум — вказівник уже націлено.
static Node *fib_minimum(FibHeap *h) { return h->min; }

// Злити дві купи: зшити кореневі списки, лишити менший min. Поглинає b.
static FibHeap *fib_union(FibHeap *a, FibHeap *b) {
    if (a->min == NULL) { free(a); return b; }
    if (b->min == NULL) { free(b); return a; }
    list_union(a->min, b->min);     // два ліси зростаються в один
    if (b->min->key < a->min->key) a->min = b->min;
    a->n += b->n;
    free(b);
    return a;
}
