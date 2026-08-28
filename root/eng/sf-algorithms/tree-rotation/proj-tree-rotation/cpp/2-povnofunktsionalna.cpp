template <typename T>
Node<T>* rotate_right(Node<T>* x, Node<T>*& root) noexcept {
    assert(x != nullptr && "Вузол x не може бути nullptr");
    assert(x->left != nullptr && "Правий поворот вимагає наявності лівого сина");

    Node<T>* y = x->left;
    Node<T>* B = y->right;

    // Крок 1: Перепідключення піддерева B
    x->left = B;
    if (B != nullptr) {
        B->parent = x;
    }

    // Крок 2: Оновлення батьківського зв'язку для y
    y->parent = x->parent;
    if (x->parent == nullptr) {
        root = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }

    // Крок 3: x стає правим сином y
    y->right = x;
    x->parent = y;

    // Крок 4: Оновлення висот знизу вгору
    update_height(x);
    update_height(y);

    return y;
}

template <typename T>
Node<T>* rotate_left(Node<T>* x, Node<T>*& root) noexcept {
    assert(x != nullptr && "Вузол x не може бути nullptr");
    assert(x->right != nullptr && "Лівий поворот вимагає наявності правого сина");

    Node<T>* y = x->right;
    Node<T>* B = y->left;

    // Крок 1: Перепідключення піддерева B
    x->right = B;
    if (B != nullptr) {
        B->parent = x;
    }

    // Крок 2: Оновлення батьківського зв'язку для y
    y->parent = x->parent;
    if (x->parent == nullptr) {
        root = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }

    // Крок 3: x стає лівим сином y
    y->left = x;
    x->parent = y;

    // Крок 4: Оновлення висот знизу вгору
    update_height(x);
    update_height(y);

    return y;
}
