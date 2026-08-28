template <typename T>
Node<T>* rotate_left_right(Node<T>* z, Node<T>*& root) noexcept {
    if (!z || !z->left) return z;
    // Крок 1: Лівий поворот для лівого сина
    z->left = rotate_left(z->left, root);
    // Крок 2: Правий поворот для кореня z
    return rotate_right(z, root);
}

template <typename T>
Node<T>* rotate_right_left(Node<T>* z, Node<T>*& root) noexcept {
    if (!z || !z->right) return z;
    // Крок 1: Правий поворот для правого сина
    z->right = rotate_right(z->right, root);
    // Крок 2: Лівий поворот для кореня z
    return rotate_left(z, root);
}
