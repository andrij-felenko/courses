Node* min_node(Node* t) { while (t->left) t = t->left; return t; }  // найлівіший

Node* erase(Node* t, int key) {
    if (!t) return nullptr;
    if      (key < t->key) t->left  = erase(t->left,  key);
    else if (key > t->key) t->right = erase(t->right, key);
    else {                                        // знайшли вузол
        if (!t->left)  { Node* r = t->right; delete t; return r; }  // 0 або 1 дитина
        if (!t->right) { Node* l = t->left;  delete t; return l; }
        Node* s = min_node(t->right);             // наступник — найлівіший справа
        t->key = s->key;                          // переносимо його ключ
        t->right = erase(t->right, s->key);       // і видаляємо наступника (легкий випадок)
    }
    return t;
}
