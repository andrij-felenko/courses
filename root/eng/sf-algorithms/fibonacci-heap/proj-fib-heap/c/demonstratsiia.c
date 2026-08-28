int main(void) {
    FibHeap *h = fib_make();
    int keys[] = {7,3,17,24,23,26,46,30,18,52,41,44,21,39,45};
    Node *n46 = NULL, *n30 = NULL;
    for (int i = 0; i < 15; i++) {
        Node *nd = fib_insert(h, keys[i]);
        if (keys[i] == 46) n46 = nd;
        if (keys[i] == 30) n30 = nd;
    }

    printf("min = %d\n", fib_minimum(h)->key);                 // 3

    Node *a = fib_extract_min(h); printf("вилучено %d\n", a->key); free(a);  // 3
    Node *b = fib_extract_min(h); printf("вилучено %d\n", b->key); free(b);  // 7

    fib_decrease_key(h, n46, 5);                               // 46 → 5
    Node *c = fib_extract_min(h); printf("вилучено %d\n", c->key); free(c);  // 5

    fib_delete(h, n30);                                        // прибрати вузол 30
    Node *d = fib_extract_min(h); printf("вилучено %d\n", d->key); free(d);  // 17

    printf("решта:");
    Node *m;
    while ((m = fib_extract_min(h)) != NULL) { printf(" %d", m->key); free(m); }
    printf("\n");
    free(h);
    return 0;
}
