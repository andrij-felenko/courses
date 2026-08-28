// Побудова дерева виразів у C++
std::unique_ptr<TreeNode> build_expression_tree(const std::string& postfix) {
    std::stack<std::unique_ptr<TreeNode>> st;

    for (char c : postfix) {
        if (c == ' ') continue;

        auto node = std::make_unique<TreeNode>(c);
        if (c == '+' || c == '-' || c == '*' || c == '/') {
            auto right = std::move(st.top()); st.pop();
            auto left = std::move(st.top()); st.pop();
            node->right = std::move(right);
            node->left = std::move(left);
        }
        st.push(std::move(node));
    }
    return std::move(st.top());
}
