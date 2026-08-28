// Ітеративний серединний обхід у C++ із використанням std::stack
std::vector<int> inorder_iterative(const TreeNode* root) {
    std::vector<int> result;
    std::stack<const TreeNode*> st;
    const TreeNode* current = root;

    while (current != nullptr || !st.empty()) {
        while (current != nullptr) {
            st.push(current);
            current = current->left.get();
        }

        current = st.top();
        st.pop();
        result.push_back(current->data);

        current = current->right.get();
    }
    return result;
}
