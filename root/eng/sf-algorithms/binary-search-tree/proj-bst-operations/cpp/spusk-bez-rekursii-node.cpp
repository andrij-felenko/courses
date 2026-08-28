Node* insert_iter(Node*& root, int key) {
    Node** p = &root;                 // p дивиться на той вказівник, який, можливо, зміниться
    while (*p) {
        Node* t = *p;
        if      (key < t->key) p = &t->left;
        else if (key > t->key) p = &t->right;
        else return t;                // ключ уже є
    }
    return *p = new Node(key);         // *p — саме та порожня комірка; сюди й садимо
}
