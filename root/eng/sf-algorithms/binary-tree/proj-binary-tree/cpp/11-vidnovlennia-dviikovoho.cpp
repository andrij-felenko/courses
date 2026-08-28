// Відбудова дерева у C++ із хеш-таблицею для O(1) пошуку індексів In-order
class TreeBuilder {
private:
    std::unordered_map<int, int> in_map;
    int pre_idx = 0;

    std::unique_ptr<TreeNode> helper(const std::vector<int>& preorder, 
                                     int in_start, int in_end) 
    {
        if (in_start > in_end) return nullptr;

        int root_val = preorder[pre_idx++];
        auto root = std::make_unique<TreeNode>(root_val);

        int in_idx = in_map[root_val];

        root->left = helper(preorder, in_start, in_idx - 1);
        root->right = helper(preorder, in_idx + 1, in_end);

        return root;
    }

public:
    std::unique_ptr<TreeNode> build(const std::vector<int>& preorder, 
                                    const std::vector<int>& inorder) 
    {
        pre_idx = 0;
        in_map.clear();
        for (int i = 0; i < (int)inorder.size(); ++i) {
            in_map[inorder[i]] = i;
        }
        return helper(preorder, 0, (int)inorder.size() - 1);
    }
};
