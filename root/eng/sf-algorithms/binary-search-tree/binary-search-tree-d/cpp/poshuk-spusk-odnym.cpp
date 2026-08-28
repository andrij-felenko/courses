struct Node {
    int   key;
    Node* left  = nullptr;
    Node* right = nullptr;
};

Node* find(Node* t, int key) {
    while (t) {
        if (key == t->key) return t;          // збіг
        t = (key < t->key) ? t->left : t->right;   // менший — ліворуч, більший — праворуч
    }
    return nullptr;                            // впали з дерева — ключа немає
}
