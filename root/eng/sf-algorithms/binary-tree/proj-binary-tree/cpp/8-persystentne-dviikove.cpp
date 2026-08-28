// Персистентний вузол у C++ із використанням std::shared_ptr
struct PersistentTreeNode {
    int data;
    std::shared_ptr<const PersistentTreeNode> left;
    std::shared_ptr<const PersistentTreeNode> right;

    PersistentTreeNode(int val, 
                       std::shared_ptr<const PersistentTreeNode> l = nullptr, 
                       std::shared_ptr<const PersistentTreeNode> r = nullptr)
        : data(val), left(std::move(l)), right(std::move(r)) {}
};

// Вставка у персистентне двійкове дерево пошуку за копіюванням шляху (Path Copying)
std::shared_ptr<const PersistentTreeNode> persistent_insert(
    const std::shared_ptr<const PersistentTreeNode>& root, int val) 
{
    if (!root) {
        return std::make_shared<const PersistentTreeNode>(val);
    }
    if (val < root->data) {
        // Копіюємо поточний вузол, оновлюючи лише ліве піддерево
        return std::make_shared<const PersistentTreeNode>(
            root->data, 
            persistent_insert(root->left, val), 
            root->right
        );
    } else {
        // Копіюємо поточний вузол, оновлюючи лише праве піддерево
        return std::make_shared<const PersistentTreeNode>(
            root->data, 
            root->left, 
            persistent_insert(root->right, val)
        );
    }
}
