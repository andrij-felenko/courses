// Прошитий вузол двійкового дерева мовою C++
struct ThreadedTreeNode {
    int data;
    ThreadedTreeNode* left = nullptr;
    ThreadedTreeNode* right = nullptr;
    bool left_is_thread = false;
    bool right_is_thread = false;

    explicit ThreadedTreeNode(int val) : data(val) {}
};

ThreadedTreeNode* left_most(ThreadedTreeNode* node) {
    if (!node) return nullptr;
    while (!node->left_is_thread && node->left) {
        node = node->left;
    }
    return node;
}

std::vector<int> threaded_inorder(ThreadedTreeNode* root) {
    std::vector<int> result;
    ThreadedTreeNode* current = left_most(root);

    while (current) {
        result.push_back(current->data);

        if (current->right_is_thread) {
            current = current->right;
        } else {
            current = left_most(current->right);
        }
    }
    return result;
}
