static void fib_cut(FibHeap *h, Node *x, Node *y) {
    // 1. Від'єднати x від дитячого кільця y.
    if (y->child == x)                          // саме x був «тим самим» вказівником?
        y->child = (x->right == x) ? NULL : x->right;   // перевести на сусіда або обнулити
    list_remove(x);
    y->degree--;
    // 2. x стає окремим деревом у кореневому списку.
    list_union(h->min, x);
    x->parent = NULL;
    x->mark = false;                            // корені не позначають
}
