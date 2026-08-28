#include <iostream>
#include <vector>
#include <optional>
#include <span>
#include <stdexcept>
#include <limits>
#include <concepts>

/* Оболонковий шаблонний клас для зваженого або бінарного графа */
template <typename T = double>
requires std::is_arithmetic_v<T>
class AdjacencyMatrix {
public:
    static constexpr T Infinity = std::numeric_limits<T>::has_infinity 
                                  ? std::numeric_limits<T>::infinity() 
                                  : std::numeric_limits<T>::max();

    explicit AdjacencyMatrix(std::size_t vertices)
        : m_vertices(vertices), m_matrix(vertices * vertices, Infinity) {
        // Заповнюємо діагональ нулями
        for (std::size_t i = 0; i < m_vertices; ++i) {
            m_matrix[i * m_vertices + i] = T{0};
        }
    }

    [[nodiscard]] std::size_t num_vertices() const noexcept {
        return m_vertices;
    }

    // Додавання орієнтованого ребра
    void add_edge(std::size_t u, std::size_t v, T weight = T{1}) {
        validate_vertex(u);
        validate_vertex(v);
        m_matrix[u * m_vertices + v] = weight;
    }

    // Додавання неорієнтованого ребра (симетричний запис)
    void add_undirected_edge(std::size_t u, std::size_t v, T weight = T{1}) {
        add_edge(u, v, weight);
        add_edge(v, u, weight);
    }

    // Видалення ребра
    void remove_edge(std::size_t u, std::size_t v) {
        validate_vertex(u);
        validate_vertex(v);
        m_matrix[u * m_vertices + v] = (u == v) ? T{0} : Infinity;
    }

    // Перевірка наявності ребра O(1)
    [[nodiscard]] bool has_edge(std::size_t u, std::size_t v) const {
        validate_vertex(u);
        validate_vertex(v);
        return m_matrix[u * m_vertices + v] != Infinity;
    }

    // Отримання ваги через std::optional
    [[nodiscard]] std::optional<T> get_weight(std::size_t u, std::size_t v) const {
        validate_vertex(u);
        validate_vertex(v);
        T w = m_matrix[u * m_vertices + v];
        if (w == Infinity) return std::nullopt;
        return w;
    }

    // Доступ до рядка матриці як std::span для cache-friendly обходу
    [[nodiscard]] std::span<const T> get_row(std::size_t u) const {
        validate_vertex(u);
        return std::span<const T>(&m_matrix[u * m_vertices], m_vertices);
    }

    // Обчислення найкоротших шляхів для всіх пар (Floyd-Warshall)
    [[nodiscard]] std::vector<T> compute_all_pairs_shortest_paths() const {
        std::vector<T> dist = m_matrix; // Копіюємо стан матриці
        const std::size_t n = m_vertices;

        for (std::size_t k = 0; k < n; ++k) {
            for (std::size_t i = 0; i < n; ++i) {
                for (std::size_t j = 0; j < n; ++j) {
                    T ik = dist[i * n + k];
                    T kj = dist[k * n + j];
                    if (ik != Infinity && kj != Infinity) {
                        if (ik + kj < dist[i * n + j]) {
                            dist[i * n + j] = ik + kj;
                        }
                    }
                }
            }
        }
        return dist;
    }

private:
    void validate_vertex(std::size_t v) const {
        if (v >= m_vertices) {
            throw std::out_of_range("Індекс вершини вийшов за межі графа");
        }
    }

    std::size_t m_vertices;
    std::vector<T> m_matrix; // Плоский неперервний буфер у купі
};

int main() {
    try {
        AdjacencyMatrix<double> graph(4);

        graph.add_edge(0, 1, 5.0);
        graph.add_edge(0, 3, 10.0);
        graph.add_edge(1, 2, 3.0);
        graph.add_edge(2, 3, 1.0);

        std::cout << "Ребро (0 -> 1): " << (graph.has_edge(0, 1) ? "Так" : "Ні") << '\n';
        std::cout << "Ребро (3 -> 0): " << (graph.has_edge(3, 0) ? "Так" : "Ні") << '\n';

        auto dist = graph.compute_all_pairs_shortest_paths();
        std::cout << "Найкоротша відстань 0 -> 3: " << dist[0 * 4 + 3] << " (маршрут 0->1->2->3)\n";

        // Обхід вихідних ребер вершини 0 через std::span
        std::cout << "Суміжні сусіди вершини 0:\n";
        auto row0 = graph.get_row(0);
        for (std::size_t v = 0; v < row0.size(); ++v) {
            if (row0[v] != graph.Infinity && v != 0) {
                std::cout << "  -> вершина " << v << " з вагою " << row0[v] << '\n';
            }
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
    }

    return 0;
}
