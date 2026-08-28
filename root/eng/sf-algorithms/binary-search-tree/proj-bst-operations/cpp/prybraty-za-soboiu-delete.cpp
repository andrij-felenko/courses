struct Node {
    int key;
    std::unique_ptr<Node> left, right;
    explicit Node(int k) : key(k) {}
};

void insert(std::unique_ptr<Node>& t, int key) {
    if (!t) { t = std::make_unique<Node>(key); return; }
    if      (key < t->key) insert(t->left,  key);
    else if (key > t->key) insert(t->right, key);
}
// коли root вийде з області видимості — усе дерево звільниться саме́.
