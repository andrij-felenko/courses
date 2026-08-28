#include <vector>

struct TreeNode {
    int key;
    TreeNode* left;
    TreeNode* right;
    explicit TreeNode(int k, TreeNode* l = nullptr, TreeNode* r = nullptr)
        : key(k), left(l), right(r) {}
};

class BstInOrderIterator {
    std::vector<TreeNode*> stack_;

    // заганяє вузол і весь його лівий хребет; вершиною стане найменший
    void pushLeft(TreeNode* node) {
        while (node != nullptr) {
            stack_.push_back(node);
            node = node->left;
        }
    }

public:
    explicit BstInOrderIterator(TreeNode* root) {
        pushLeft(root);              // інваріант ставимо ще до першого next()
    }

    bool hasNext() const {
        return !stack_.empty();      // порожній стек — обхід вичерпано
    }

    int next() {
        TreeNode* node = stack_.back();  // вершина — найменший ще не відданий ключ
        stack_.pop_back();
        pushLeft(node->right);           // тепер лівий хребет його правого піддерева
        return node->key;
    }
};
