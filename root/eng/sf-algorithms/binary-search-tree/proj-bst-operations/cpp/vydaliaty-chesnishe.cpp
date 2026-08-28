Node* erase_splice(Node* t, int key) {
    if (!t) return nullptr;
    if      (key < t->key) t->left  = erase_splice(t->left,  key);
    else if (key > t->key) t->right = erase_splice(t->right, key);
    else {
        if (!t->left)  { Node* r = t->right; delete t; return r; }
        if (!t->right) { Node* l = t->left;  delete t; return l; }
        Node* par = t, *s = t->right;          // шукаємо наступника й ЙОГО батька
        while (s->left) { par = s; s = s->left; }
        if (par != t) { par->left = s->right;  s->right = t->right; }
        // (якщо par == t, наступник — прямий правий син: його right уже на місці)
        s->left = t->left;                     // наступник переймає піддерева жертви
        delete t;
        return s;                              // і стає новим коренем піддерева
    }
    return t;
}
