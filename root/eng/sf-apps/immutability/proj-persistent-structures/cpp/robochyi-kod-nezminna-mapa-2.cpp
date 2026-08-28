// Лівий поворот навколо x: правий син y підіймається над x.
//        x                 y
//       / \               / \
//      a   y     ==>     x   c
//         / \           / \
//        b   c         a   b
// Будуємо ДВА нові вузли (x' і y'); піддерева a, b, c — беруться як є (спільні).
template <typename K, typename V>
Tree<K, V> rotateLeft(const Tree<K, V>& x) {
    const auto& y = x->right;
    auto x2 = mk(x->key, x->val, x->left, y->left);      // новий x з піддеревами a, b
    return   mk(y->key, y->val, x2,      y->right);      // новий y над x2 і c
}

// Правий поворот — дзеркально.
template <typename K, typename V>
Tree<K, V> rotateRight(const Tree<K, V>& y) {
    const auto& x = y->left;
    auto y2 = mk(y->key, y->val, x->right, y->right);    // новий y з піддеревами b, c
    return   mk(x->key, x->val, x->left,  y2);           // новий x над a і y2
}
