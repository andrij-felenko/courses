// Вставити (чи оновити) ключ. Повертає НОВИЙ корінь; старе дерево ціле.
template <typename K, typename V>
Tree<K, V> insert(const Tree<K, V>& t, K k, V v) {
    if (!t)                                      // дійшли до порожнього місця — новий лист
        return mk(std::move(k), std::move(v), Tree<K, V>{}, Tree<K, V>{});

    if (k < t->key)                              // ключ ліворуч: перебудовуємо лівий бік,
        return balance(mk(t->key, t->val,        //   ПРАВИЙ беремо як є (спільний!)
                          insert(t->left, std::move(k), std::move(v)),
                          t->right));
    if (t->key < k)                              // ключ праворуч: дзеркально
        return balance(mk(t->key, t->val,
                          t->left,
                          insert(t->right, std::move(k), std::move(v))));

    // ключ той самий — оновлюємо значення (новий вузол із тими самими дітьми)
    return mk(std::move(k), std::move(v), t->left, t->right);
}
