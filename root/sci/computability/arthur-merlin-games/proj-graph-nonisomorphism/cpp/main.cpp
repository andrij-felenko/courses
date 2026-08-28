#include <iostream>
#include <vector>
#include <numeric>
#include <random>
#include <algorithm>
#include <stdexcept>

class Graph {
private:
    std::size_t num_vertices_;
    std::vector<std::vector<bool>> adj_;

public:
    explicit Graph(std::size_t n)
        : num_vertices_(n), adj_(n, std::vector<bool>(n, false)) {}

    std::size_t size() const noexcept { return num_vertices_; }

    void add_edge(std::size_t u, std::size_t v) {
        if (u >= num_vertices_ || v >= num_vertices_) {
            throw std::out_of_range("Вершина виходить за межі графа");
        }
        adj_[u][v] = true;
        adj_[v][u] = true;
    }

    bool has_edge(std::size_t u, std::size_t v) const noexcept {
        return adj_[u][v];
    }

    /* Застосування перестановки до вершин графа */
    Graph permute(const std::vector<std::size_t>& perm) const {
        Graph h(num_vertices_);
        for (std::size_t i = 0; i < num_vertices_; ++i) {
            for (std::size_t j = 0; j < num_vertices_; ++j) {
                if (adj_[i][j]) {
                    h.adj_[perm[i]][perm[j]] = true;
                }
            }
        }
        return h;
    }
};

/* Клас оракула Мерліна для визначення ізоморфізму */
class MerlinOracle {
private:
    static bool is_isomorphic_recursive(const Graph& g1, const Graph& g2,
                                         std::vector<std::size_t>& perm,
                                         std::vector<bool>& used,
                                         std::size_t depth) {
        const std::size_t n = g1.size();
        if (depth == n) {
            for (std::size_t i = 0; i < n; ++i) {
                for (std::size_t j = 0; j < n; ++j) {
                    if (g1.has_edge(i, j) != g2.has_edge(perm[i], perm[j])) {
                        return false;
                    }
                }
            }
            return true;
        }

        for (std::size_t i = 0; i < n; ++i) {
            if (!used[i]) {
                used[i] = true;
                perm[depth] = i;
                if (is_isomorphic_recursive(g1, g2, perm, used, depth + 1)) {
                    return true;
                }
                used[i] = false;
            }
        }
        return false;
    }

public:
    static bool check_isomorphism(const Graph& g1, const Graph& g2) {
        const std::size_t n = g1.size();
        std::vector<std::size_t> perm(n);
        std::vector<bool> used(n, false);
        return is_isomorphic_recursive(g1, g2, perm, used, 0);
    }

    /* Мерлін визначає, якому з двох кандидатів відповідає викликовий граф H */
    static std::size_t identify_graph(const Graph& g0, const Graph& g1, const Graph& h) {
        if (check_isomorphism(g0, h)) return 0;
        if (check_isomorphism(g1, h)) return 1;
        return 0; /* Оракул не знайшов збігу */
    }
};

/* Клас верифікатора Артура */
class ArthurVerifier {
private:
    std::mt19937 rng_;

public:
    ArthurVerifier() : rng_(std::random_device{}()) {}

    bool execute_round(const Graph& g0, const Graph& g1) {
        const std::size_t n = g0.size();

        /* 1. Артур обирає випадковий біт b ∈ {0, 1} */
        std::uniform_int_distribution<std::size_t> dist(0, 1);
        std::size_t b = dist(rng_);

        /* 2. Генерація випадкової перестановки */
        std::vector<std::size_t> perm(n);
        std::iota(perm.begin(), perm.end(), 0);
        std::shuffle(perm.begin(), perm.end(), rng_);

        /* 3. Створення викликового графа H = π(G_b) */
        const Graph& selected_graph = (b == 0) ? g0 : g1;
        Graph h = selected_graph.permute(perm);

        /* 4. Мерлін надсилає відповідь */
        std::size_t merlin_response = MerlinOracle::identify_graph(g0, g1, h);

        /* 5. Перевірка відповіді */
        return (merlin_response == b);
    }

    bool verify_non_isomorphism(const Graph& g0, const Graph& g1, std::size_t rounds) {
        for (std::size_t r = 1; r <= rounds; ++r) {
            if (!execute_round(g0, g1)) {
                std::cout << "Раунд " << r << ": Відхилено Артуром! Графи ізоморфні.\n";
                return false;
            }
        }
        std::cout << "Успіх! " << rounds << " раундів підтвердили неізоморфність.\n";
        return true;
    }
};

int main() {
    try {
        Graph g0(4);
        g0.add_edge(0, 1); g0.add_edge(1, 2);
        g0.add_edge(2, 3); g0.add_edge(3, 0); // C4

        Graph g1(4);
        g1.add_edge(0, 1); g1.add_edge(0, 2);
        g1.add_edge(0, 3); // K_1,3

        ArthurVerifier arthur;

        std::cout << "--- Тест 1: Неізоморфні графи ---\n";
        arthur.verify_non_isomorphism(g0, g1, 10);

        std::cout << "\n--- Тест 2: Ізоморфні графи ---\n";
        std::vector<std::size_t> p = {1, 2, 3, 0};
        Graph g0_iso = g0.permute(p);
        arthur.verify_non_isomorphism(g0, g0_iso, 10);

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
