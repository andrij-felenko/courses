/* Подвійний Left-Right поворот (зигзаг) навколо z */
Node* rotate_left_right(Node* z, Node** root) {
    if (!z || !z->left) return z;
    /* Крок 1: Лівий поворот для лівого сина, щоб випрямити зигзаг у LL */
    z->left = rotate_left(z->left, root);
    /* Крок 2: Правий поворот для кореня z */
    return rotate_right(z, root);
}

/* Подвійний Right-Left поворот (заг-зиг) навколо z */
Node* rotate_right_left(Node* z, Node** root) {
    if (!z || !z->right) return z;
    /* Крок 1: Правий поворот для правого сина, щоб випрямити заг-зиг у RR */
    z->right = rotate_right(z->right, root);
    /* Крок 2: Лівий поворот для кореня z */
    return rotate_left(z, root);
}
