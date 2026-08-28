template <typename K, typename V>
const V* find(const Tree<K, V>& t, const K& k) {
    const TNode<K, V>* cur = t.get();
    while (cur) {
        if      (k < cur->key) cur = cur->left.get();
        else if (cur->key < k) cur = cur->right.get();
        else                   return &cur->val;      // знайшли
    }
    return nullptr;                                    // немає такого ключа
}
