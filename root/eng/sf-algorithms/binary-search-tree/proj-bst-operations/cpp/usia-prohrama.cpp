#include <cstdio>

struct Node {
    int   key;
    Node* left  = nullptr;
    Node* right = nullptr;
    explicit Node(int k) : key(k) {}
};

// Пошук: цикл до збігу або до пустки. O(h).
Node* find(Node* t, int key) {
    while (t && t->key != key)
        t = (key < t->key) ? t->left : t->right;
    return t;                       // вузол або nullptr
}

// Вставка: спуск + новий листок; повертає корінь піддерева. O(h).
Node* insert(Node* t, int key) {
    if (!t) return new Node(key);              // місце знайдено
    if      (key < t->key) t->left  = insert(t->left,  key);
    else if (key > t->key) t->right = insert(t->right, key);
    return t;                                  // key == t->key: дублікат ігноруємо
}

// Найлівіший вузол піддерева — in-order-наступник. O(h).
Node* min_node(Node* t) { while (t->left) t = t->left; return t; }

// Видалення: три випадки, двоє дітей — через наступника. O(h).
Node* erase(Node* t, int key) {
    if (!t) return nullptr;
    if      (key < t->key) t->left  = erase(t->left,  key);
    else if (key > t->key) t->right = erase(t->right, key);
    else {                                     // знайшли вузол
        if (!t->left)  { Node* r = t->right; delete t; return r; }   // 0/1 дитина
        if (!t->right) { Node* l = t->left;  delete t; return l; }
        Node* s = min_node(t->right);          // наступник
        t->key   = s->key;                     // копіюємо його ключ у нашу діру
        t->right = erase(t->right, s->key);    // і зносимо наступника (легкий випадок)
    }
    return t;
}

// Симетричний обхід: ліве, вузол, праве → ключі за зростанням. O(n).
void inorder(Node* t) {
    if (!t) return;
    inorder(t->left);
    printf("%d ", t->key);
    inorder(t->right);
}

// Висота: найдовший шлях у РЕБРАХ; порожнє дерево = -1, лист = 0. O(n).
int height(Node* t) {
    if (!t) return -1;
    int l = height(t->left);
    int r = height(t->right);
    return 1 + (l > r ? l : r);
}

// Знесення: спершу обидві дитини, потім сам вузол (post-order). O(n).
void destroy(Node* t) {
    if (!t) return;
    destroy(t->left);
    destroy(t->right);
    delete t;
}

int main() {
    Node* root = nullptr;
    int keys[] = {50, 30, 70, 20, 40, 60, 80, 35, 45};
    for (int k : keys) root = insert(root, k);

    printf("in-order: ");    inorder(root); printf("\n");
    printf("height  : %d\n", height(root));
    printf("find 45 : %s\n", find(root, 45) ? "є" : "нема");

    root = erase(root, 30);          // вузол із двома дітьми
    printf("after 30: ");    inorder(root); printf("\n");

    destroy(root);                   // повернути всю пам'ять
    return 0;
}
