// Ідіоматичний вузол двійкового дерева мовою C++ (RAII)
#include <memory>

struct TreeNode {
    int data;
    std::unique_ptr<TreeNode> left;
    std::unique_ptr<TreeNode> right;

    explicit TreeNode(int val) 
        : data(val), left(nullptr), right(nullptr) {}
};
