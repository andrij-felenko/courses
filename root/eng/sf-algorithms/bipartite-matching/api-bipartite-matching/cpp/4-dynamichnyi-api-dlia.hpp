// C++20 API: Динамічне оновлення графа
namespace graph::matching {

class DynamicBipartiteMatching {
public:
    DynamicBipartiteMatching(std::size_t u_size, std::size_t v_size);
    ~DynamicBipartiteMatching() noexcept = default;

    // Інкрементне додавання ребра (u, v)
    // Якщо паросполучення можна збільшити за 1 прохід DFS, воно збільшується за O(V + E)
    bool insert_edge(std::size_t u, std::size_t v);

    // Видалення ребра (u, v)
    // Якщо ребро належало паросполученню, шукається локальний заміщаючий шлях
    bool remove_edge(std::size_t u, std::size_t v);

    // Отримання поточного розміру паросполучення за O(1)
    [[nodiscard]] std::size_t matching_size() const noexcept;

    // Перевірка: чи покрита вершина u у поточній конфігурації
    [[nodiscard]] bool is_u_matched(std::size_t u) const;
    [[nodiscard]] bool is_v_matched(std::size_t v) const;
};

} // namespace graph::matching
