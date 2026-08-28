static const int RATIO = 3;   // допустима перевага одного боку над братом

template <typename K, typename V>
Tree<K, V> balance(const Tree<K, V>& t) {
    int ls = TNode<K, V>::sz(t->left);
    int rs = TNode<K, V>::sz(t->right);

    if (rs > RATIO * ls + 1) {                  // правий бік надто важкий
        const auto& r = t->right;
        if (TNode<K, V>::sz(r->left) > TNode<K, V>::sz(r->right))
            // зиґзаґ: правий син «нахилений» вліво — спершу випрямити його
            return rotateLeft(mk(t->key, t->val, t->left, rotateRight(r)));
        return rotateLeft(t);                   // прямий випадок — один поворот
    }
    if (ls > RATIO * rs + 1) {                  // лівий бік надто важкий — дзеркально
        const auto& l = t->left;
        if (TNode<K, V>::sz(l->right) > TNode<K, V>::sz(l->left))
            return rotateRight(mk(t->key, t->val, rotateLeft(l), t->right));
        return rotateRight(t);
    }
    return t;                                    // баланс у нормі — вузол лишається як є
}
