/**
 * @file TreeExplorer.hpp
 * @brief Об'єктно-орієнтований C++20 шаблонний API для безпечної навігації в нескінченних деревах.
 */

#ifndef TREE_EXPLORER_HPP
#define TREE_EXPLORER_HPP

#include <concepts>
#include <vector>
#include <queue>
#include <optional>
#include <expected>
#include <functional>
#include <memory>
#include <algorithm>

namespace tree_analysis {

template<typename T>
concept LocallyFiniteState = requires(const T& node) {
    { node.get_children() } -> std::same_as<std::vector<T>>;
    { node.is_goal() } -> std::same_as<bool>;
};

enum class SearchStatus {
    TargetFound,
    TargetNotFound,
    MaxVisitedExceeded,
    MaxDepthExceeded
};

struct SearchStats {
    size_t visited_nodes{0};
    size_t max_depth_reached{0};
};

template<LocallyFiniteState StateType>
class TreeExplorer {
public:
    enum class Strategy {
        BFS,
        IDDFS
    };

    struct Options {
        Strategy strategy{Strategy::BFS};
        size_t max_visited{100000};
        size_t max_depth{1000};
    };

    explicit TreeExplorer(Options options = {}) : options_(options) {}

    [[nodiscard]] std::expected<StateType, SearchStatus> search(const StateType& root) {
        stats_ = {};
        if (options_.strategy == Strategy::BFS) {
            return search_bfs(root);
        } else {
            return search_iddfs(root);
        }
    }

    [[nodiscard]] const SearchStats& stats() const noexcept {
        return stats_;
    }

private:
    Options options_;
    SearchStats stats_;

    std::expected<StateType, SearchStatus> search_bfs(const StateType& root) {
        std::queue<std::pair<StateType, size_t>> q;
        q.push({root, 0});

        while (!q.empty()) {
            if (stats_.visited_nodes >= options_.max_visited) {
                return std::unexpected(SearchStatus::MaxVisitedExceeded);
            }

            auto [current, depth] = q.front();
            q.pop();
            stats_.visited_nodes++;
            stats_.max_depth_reached = std::max(stats_.max_depth_reached, depth);

            if (current.is_goal()) {
                return current;
            }

            if (depth < options_.max_depth) {
                for (auto&& child : current.get_children()) {
                    q.push({std::move(child), depth + 1});
                }
            }
        }
        return std::unexpected(SearchStatus::TargetNotFound);
    }

    std::expected<StateType, SearchStatus> search_iddfs(const StateType& root) {
        for (size_t limit = 0; limit <= options_.max_depth; ++limit) {
            auto res = dfs_bounded(root, 0, limit);
            if (res.has_value()) return res;
            if (stats_.visited_nodes >= options_.max_visited) {
                return std::unexpected(SearchStatus::MaxVisitedExceeded);
            }
        }
        return std::unexpected(SearchStatus::TargetNotFound);
    }

    std::optional<StateType> dfs_bounded(const StateType& current, size_t depth, size_t limit) {
        stats_.visited_nodes++;
        stats_.max_depth_reached = std::max(stats_.max_depth_reached, depth);

        if (current.is_goal()) return current;

        if (depth < limit) {
            for (const auto& child : current.get_children()) {
                auto res = dfs_bounded(child, depth + 1, limit);
                if (res.has_value()) return res;
            }
        }
        return std::nullopt;
    }
};

} // namespace tree_analysis

#endif // TREE_EXPLORER_HPP
