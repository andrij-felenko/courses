// Побудова топології двійкового дерева за порядковим індексом (Unranking) мовою C++ (RAII)
#include <memory>
#include <vector>
#include <cstdint>

struct TreeStructureNode {
    std::unique_ptr<TreeStructureNode> left;
    std::unique_ptr<TreeStructureNode> right;
};

std::unique_ptr<TreeStructureNode> unrank_binary_tree(
    std::size_t n, 
    std::uint64_t rank, 
    const std::vector<std::uint64_t>& catalan_table) 
{
    if (n == 0) {
        return nullptr;
    }

    auto root = std::make_unique<TreeStructureNode>();
    for (std::size_t left_size = 0; left_size < n; ++left_size) {
        std::size_t right_size = n - 1 - left_size;
        std::uint64_t count = catalan_table[left_size] * catalan_table[right_size];

        if (rank < count) {
            std::uint64_t left_rank = rank / catalan_table[right_size];
            std::uint64_t right_rank = rank % catalan_table[right_size];
            root->left = unrank_binary_tree(left_size, left_rank, catalan_table);
            root->right = unrank_binary_tree(right_size, right_rank, catalan_table);
            return root;
        }
        rank -= count;
    }
    return root;
}
