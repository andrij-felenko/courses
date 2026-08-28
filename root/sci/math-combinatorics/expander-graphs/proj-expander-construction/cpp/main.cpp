#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <array>
#include <numeric>
#include <iomanip>

struct Vertex {
    int x{0};
    int y{0};

    bool operator==(const Vertex& other) const {
        return x == other.x && y == other.y;
    }
};

class MargulisExpander {
public:
    explicit MargulisExpander(int m) : m_grid_size(m), m_num_vertices(m * m) {}

    [[nodiscard]] int grid_size() const noexcept { return m_grid_size; }
    [[nodiscard]] int num_vertices() const noexcept { return m_num_vertices; }
    [[nodiscard]] static constexpr int degree() noexcept { return 8; }

    [[nodiscard]] std::array<Vertex, 8> get_neighbors(Vertex v) const noexcept {
        const int x = v.x;
        const int y = v.y;
        const int m = m_grid_size;

        auto mod_m = [m](int a) noexcept -> int {
            int r = a % m;
            return r < 0 ? r + m : r;
        };

        return std::array<Vertex, 8>{
            Vertex{x, mod_m(y + x)},
            Vertex{x, mod_m(y - x)},
            Vertex{x, mod_m(y + x + 1)},
            Vertex{x, mod_m(y - x - 1)},
            Vertex{mod_m(x + y), y},
            Vertex{mod_m(x - y), y},
            Vertex{mod_m(x + y + 1), y},
            Vertex{mod_m(x - y - 1), y}
        };
    }

    [[nodiscard]] std::vector<Vertex> random_walk(Vertex start, size_t steps) const {
        std::vector<Vertex> path;
        path.reserve(steps + 1);
        path.push_back(start);

        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<size_t> dist(0, 7);

        Vertex current = start;
        for (size_t i = 0; i < steps; ++i) {
            auto neighbors = get_neighbors(current);
            current = neighbors[dist(gen)];
            path.push_back(current);
        }
        return path;
    }

    [[nodiscard]] double compute_spectral_gap(size_t max_iterations = 500, double tol = 1e-6) const {
        const size_t N = m_num_vertices;
        std::vector<double> v(N);

        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<double> dist(-0.5, 0.5);

        for (auto& val : v) {
            val = dist(gen);
        }

        project_perpendicular_to_v1(v);
        normalize_vector(v);

        double lambda2 = 0.0;
        std::vector<double> next_v(N, 0.0);

        for (size_t iter = 0; iter < max_iterations; ++iter) {
            std::fill(next_v.begin(), next_v.end(), 0.0);

            for (size_t idx = 0; idx < N; ++idx) {
                Vertex cur{static_cast<int>(idx / m_grid_size), static_cast<int>(idx % m_grid_size)};
                auto neighbors = get_neighbors(cur);
                for (const auto& n : neighbors) {
                    size_t n_idx = static_cast<size_t>(n.x * m_grid_size + n.y);
                    next_v[n_idx] += v[idx];
                }
            }

            project_perpendicular_to_v1(next_v);

            double rayleigh = 0.0;
            for (size_t i = 0; i < N; ++i) {
                rayleigh += v[i] * next_v[i];
            }

            normalize_vector(next_v);

            double diff = std::abs(rayleigh - lambda2);
            lambda2 = rayleigh;
            v = next_v;

            if (diff < tol) {
                break;
            }
        }

        return static_cast<double>(degree()) - lambda2;
    }

private:
    int m_grid_size;
    int m_num_vertices;

    static void normalize_vector(std::vector<double>& vec) noexcept {
        double norm = 0.0;
        for (double val : vec) {
            norm += val * val;
        }
        norm = std::sqrt(norm);
        if (norm > 1e-12) {
            for (double& val : vec) {
                val /= norm;
            }
        }
    }

    static void project_perpendicular_to_v1(std::vector<double>& vec) noexcept {
        double sum = std::accumulate(vec.begin(), vec.end(), 0.0);
        double avg = sum / static_cast<double>(vec.size());
        for (double& val : vec) {
            val -= avg;
        }
    }
};

int main() {
    std::cout << std::fixed << std::setprecision(6);
    int m = 12;
    MargulisExpander expander(m);

    std::cout << "=== C++ Реалізація графа Маргуліса — Габбера — Галіля ===" << std::endl;
    std::cout << "Розмір сітки m = " << m << ", Вершин N = " << expander.num_vertices() << std::endl;

    Vertex start{0, 0};
    auto neighbors = expander.get_neighbors(start);
    std::cout << "\nСусіди вершини (0, 0):" << std::endl;
    for (size_t i = 0; i < neighbors.size(); ++i) {
        std::cout << "  [" << i + 1 << "] (" << neighbors[i].x << ", " << neighbors[i].y << ")\n";
    }

    double gap = expander.compute_spectral_gap();
    double lambda2 = static_cast<double>(expander.degree()) - gap;

    std::cout << "\nРезультати спектрального аналізу:" << std::endl;
    std::cout << "  Степінь d = " << expander.degree() << std::endl;
    std::cout << "  λ₂ = " << lambda2 << std::endl;
    std::cout << "  Спектральна щілина γ = d - λ₂ = " << gap << std::endl;

    return 0;
}
