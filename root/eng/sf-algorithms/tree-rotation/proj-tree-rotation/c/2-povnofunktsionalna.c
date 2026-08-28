/* Правий поворот навколо вузла x */
Node* rotate_right(Node* x, Node** root) {
    assert(x != NULL && "Вузол x не може бути NULL");
    assert(x->left != NULL && "Правий поворот вимагає наявності лівого сина");

    Node* y = x->left;
    Node* B = y->right;

    /* Крок 1: Перепідключення правого піддерева B до x */
    x->left = B;
    if (B != NULL) {
        B->parent = x;
    }

    /* Крок 2: Зв'язування y з батьком вузла x (P) */
    y->parent = x->parent;
    if (x->parent == NULL) {
        if (root != NULL) {
            *root = y; /* y стає новим коренем усього дерева */
        }
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }

    /* Крок 3: Переміщення x у правого сина y */
    y->right = x;
    x->parent = y;

    /* Крок 4: Оновлення метрик (строго знизу вгору: спочатку x, потім y) */
    update_height(x);
    update_height(y);

    return y; /* Повертаємо новий корінь піддерева */
}

/* Лівий поворот навколо вузла x */
Node* rotate_left(Node* x, Node** root) {
    assert(x != NULL && "Вузол x не може бути NULL");
    assert(x->right != NULL && "Лівий поворот вимагає наявності правого сина");

    Node* y = x->right;
    Node* B = y->left;

    /* Крок 1: Перепідключення лівого піддерева B до x */
    x->right = B;
    if (B != NULL) {
        B->parent = x;
    }

    /* Крок 2: Зв'язування y з батьком вузла x (P) */
    y->parent = x->parent;
    if (x->parent == NULL) {
        if (root != NULL) {
            *root = y; /* y стає новим коренем усього дерева */
        }
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }

    /* Крок 3: Переміщення x у лівого сина y */
    y->left = x;
    x->parent = y;

    /* Крок 4: Оновлення метрик (строго знизу вгору: спочатку x, потім y) */
    update_height(x);
    update_height(y);

    return y;
}
