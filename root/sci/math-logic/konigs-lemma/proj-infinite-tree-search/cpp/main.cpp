#include <iostream>
#include <vector>
#include <queue>
#include <memory>
#include <optional>
#include <functional>

struct TreeNode {
    int id;
    int depth;
    bool is_infinite_branch;

    [[nodiscard]] std::vector<TreeNode> get_children() const {
        std::vector<TreeNode> children;
        if (is_infinite_branch) {
            children.push_back({ id * 2, depth + 1, true });
            children.push_back({ id * 2 + 1, depth + 1, false });
        } else {
            if (depth % 3 != 0) {
                children.push_back({ id * 2, depth + 1, false });
            }
        }
        return children;
    }

    [[nodiscard]] bool is_goal() const noexcept {
        return depth == 3 && !is_infinite_branch;
    }
};

class InfiniteTreeSearcher {
public:
    explicit InfiniteTreeSearcher(TreeNode root) : root_(root) {}

    std::optional<TreeNode> search_bfs(size_t max_steps) {
        std::queue<TreeNode> q;
        q.push(root_);
        size_t visited = 0;

        while (!q.empty() && visited < max_steps) {
            TreeNode current = q.front();
            q.pop();
            visited++;

            if (current.is_goal()) {
                std::cout << "[BFS C++] УСПІХ! Ціль знайдено на глибині " << current.depth 
                          << " післяперевірки " << visited << " вузлів.\n";
                return current;
            }

            for (const auto& child : current.get_children()) {
                q.push(child);
            }
        }
        return std::nullopt;
    }

    std::optional<TreeNode> search_dfs(size_t max_steps) {
        size_t visited = 0;
        return dfs_recursive(root_, visited, max_steps);
    }

private:
    TreeNode root_;

    std::optional<TreeNode> dfs_recursive(const TreeNode& current, size_t& visited, size_t max_steps) {
        visited++;
        if (visited >= max_steps) return std::nullopt;

        if (current.is_goal()) return current;

        for (const auto& child : current.get_children()) {
            auto res = dfs_recursive(child, visited, max_steps);
            if (res.has_value()) return res;
        }
        return std::nullopt;
    }
};

int main() {
    TreeNode root{ 1, 0, true };
    InfiniteTreeSearcher searcher(root);

    std::cout << "=== СИМУЛЯЦІЯ ОБХОДУ НЕСКІНЧЕННИХ ДЕРЕВ (C++20) ===\n\n";

    if (auto res = searcher.search_bfs(500)) {
        std::cout << "[C++] BFS довів повноту обходу локально скінченних рівнів.\n";
    }

    if (auto res = searcher.search_dfs(100); !res.has_value()) {
        std::cout << "[C++] DFS застряг у нескінченній гілці (порушення гарантії завершуваності).\n";
    }

    return 0;
}
