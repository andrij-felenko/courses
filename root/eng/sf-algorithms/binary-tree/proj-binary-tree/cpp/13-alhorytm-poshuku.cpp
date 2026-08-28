// Пошук найменшого спільного предка (LCA) у C++ з сирими вказівниками
const TreeNode* lowest_common_ancestor(const TreeNode* root, 
                                      const TreeNode* p, 
                                      const TreeNode* q) 
{
    if (!root || root == p || root == q) {
        return root;
    }

    const TreeNode* left_lca = lowest_common_ancestor(root->left.get(), p, q);
    const TreeNode* right_lca = lowest_common_ancestor(root->right.get(), p, q);

    if (left_lca && right_lca) {
        return root;
    }

    return left_lca ? left_lca : right_lca;
}
