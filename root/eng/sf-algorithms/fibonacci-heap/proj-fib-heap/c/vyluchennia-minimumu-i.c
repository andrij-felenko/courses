static void fib_consolidate(FibHeap *h) {
    int Dn = max_degree(h->n);
    Node **A = calloc(Dn + 1, sizeof(Node *));   // A[d] — корінь степеня d або NULL

    // Знімок кореневого списку (linking переплете кільце на ходу).
    int nroots = 0;
    Node *w = h->min;
    do { nroots++; w = w->right; } while (w != h->min);
    Node **roots = malloc(nroots * sizeof(Node *));
    w = h->min;
    for (int i = 0; i < nroots; i++) { roots[i] = w; w = w->right; }

    // Розкладаємо дерева за степенем; двоє одного степеня — зчіплюємо.
    for (int i = 0; i < nroots; i++) {
        Node *x = roots[i];
        int d = x->degree;
        while (A[d] != NULL) {
            Node *y = A[d];                       // уже є дерево степеня d
            if (y->key < x->key) { Node *t = x; x = y; y = t; }  // x — менший ключ
            fib_link(y, x);                       // y під x; степінь x виріс
            A[d] = NULL;
            d++;                                  // переїхали в наступну комірку
        }
        A[d] = x;
    }

    // Зібрати кореневий список наново з масиву й заново знайти min.
    h->min = NULL;
    for (int i = 0; i <= Dn; i++) {
        if (A[i] == NULL) continue;
        A[i]->left = A[i]->right = A[i];          // від'єднати від старих сусідів
        if (h->min == NULL) h->min = A[i];
        else {
            list_union(h->min, A[i]);
            if (A[i]->key < h->min->key) h->min = A[i];
        }
    }
    free(A);  free(roots);
}
