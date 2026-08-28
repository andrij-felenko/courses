template <typename T = double>
requires std::is_arithmetic_v<T>
class AdjacencyMatrix {
public:
    // Конструктор ініціалізації розміру графа
    explicit AdjacencyMatrix(std::size_t vertices);

    // Модифікатори графа
    void add_edge(std::size_t u, std::size_t v, T weight = T{1});
    void add_undirected_edge(std::size_t u, std::size_t v, T weight = T{1});
    void remove_edge(std::size_t u, std::size_t v);

    // Селектори та перевірки стану
    [[nodiscard]] bool has_edge(std::size_t u, std::size_t v) const;
    [[nodiscard]] std::optional<T> get_weight(std::size_t u, std::size_t v) const;
    [[nodiscard]] std::span<const T> get_row(std::size_t u) const;

    // Метрики вершин
    [[nodiscard]] std::size_t num_vertices() const noexcept;
    [[nodiscard]] std::size_t out_degree(std::size_t u) const;
    [[nodiscard]] std::size_t in_degree(std::size_t v) const;

    // Алгоритми аналізу
    [[nodiscard]] std::vector<T> compute_all_pairs_shortest_paths() const;
};
