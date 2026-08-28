#include <vector>
#include <iostream>

struct ClosureEntry {
    int ancestor_id;
    int descendant_id;
    int depth;
};

std::vector<ClosureEntry> generate_closure(const TreeNode* root) {
    std::vector<ClosureEntry> entries;

    auto collect = [&](auto& self, const TreeNode* node) -> void {
        if (!node) return;

        // Рефлексивний запис нульової глибини
        entries.push_back({node->id, node->id, 0});

        // Ітерація по всіх предках вгору до кореня
        const TreeNode* parent_ptr = node->parent;
        int d = 1;
        while (parent_ptr) {
            entries.push_back({parent_ptr->id, node->id, d});
            parent_ptr = parent_ptr->parent;
            ++d;
        }

        for (const auto& child : node->children) {
            self(self, child.get());
        }
    };

    collect(collect, root);
    return entries;
}
