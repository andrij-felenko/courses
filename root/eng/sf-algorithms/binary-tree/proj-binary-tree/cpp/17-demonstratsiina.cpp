int main() {
    // Побудова того самого дерева в C++ з авто-управлінням пам'яттю
    auto root = TreeNode::make(1);
    root->left = TreeNode::make(2);
    root->right = TreeNode::make(3);
    root->left->left = TreeNode::make(4);
    root->left->right = TreeNode::make(5);

    std::cout << "Кількість вузлів: " << count_nodes(root.get()) << "\n";
    std::cout << "Висота дерева: " << tree_height(root.get()) << "\n";

    std::vector<int> inorder_vals;
    collect_inorder(root.get(), inorder_vals);
    
    std::cout << "In-order (рекурсія): ";
    for (int val : inorder_vals) {
        std::cout << val << " ";
    }
    std::cout << "\n";

    auto iter_vals = inorder_iterative(root.get());
    std::cout << "In-order (ітеративно): ";
    for (int val : iter_vals) {
        std::cout << val << " ";
    }
    std::cout << "\n";

    auto levels = level_order(root.get());
    std::cout << "Рівні дерева (BFS):\n";
    for (size_t i = 0; i < levels.size(); ++i) {
        std::cout << "  Рівень " << i << ": ";
        for (int v : levels[i]) std::cout << v << " ";
        std::cout << "\n";
    }

    const TreeNode* lca = lowest_common_ancestor(root.get(), 
                                                root->left->left.get(), 
                                                root->left->right.get());
    std::cout << "LCA вузлів 4 та 5: " << (lca ? lca->data : -1) << "\n";

    // Пам'ять звільниться сама при виході з функції завдяки std::unique_ptr
    return 0;
}
