// C++ Implementation: Kuhn's Algorithm using Modern C++ Standard Containers
#include <vector>
#include <utility>
#include <iostream>
#include <cstddef>
#include <algorithm>

class KuhnMatcher {
public:
    KuhnMatcher(std::size_t left_size, std::size_t right_size)
        : n1_(left_size), n2_(right_size), adj_(left_size), match_v_(right_size, -1) {}

    void add_edge(std::size_t u_left, std::size_t v_right) {
        adj_.at(u_left).push_back(v_right);
    }

    // Обчислює максимальне паросполучення і повертає список пар (u_left, v_right)
    [[nodiscard]] std::vector<std::pair<std::size_t, std::size_t>> find_max_matching() {
        std::fill(match_v_.begin(), match_v_.end(), -1);
        std::vector<bool> visited(n1_, false);

        for (std::size_t u = 0; u < n1_; ++u) {
            std::fill(visited.begin(), visited.end(), false);
            try_augment(u, visited);
        }

        std::vector<std::pair<std::size_t, std::size_t>> matching;
        for (std::size_t v = 0; v < n2_; ++v) {
            if (match_v_[v] != -1) {
                matching.emplace_back(static_cast<std::size_t>(match_v_[v]), v);
            }
        }
        return matching;
    }

private:
    bool try_augment(std::size_t u, std::vector<bool>& visited) {
        if (visited[u]) return false;
        visited[u] = true;

        for (std::size_t v : adj_[u]) {
            if (match_v_[v] == -1 || try_augment(static_cast<std::size_t>(match_v_[v]), visited)) {
                match_v_[v] = static_cast<int>(u);
                return true;
            }
        }
        return false;
    }

    std::size_t n1_;
    std::size_t n2_;
    std::vector<std::vector<std::size_t>> adj_;
    std::vector<int> match_v_;
};
