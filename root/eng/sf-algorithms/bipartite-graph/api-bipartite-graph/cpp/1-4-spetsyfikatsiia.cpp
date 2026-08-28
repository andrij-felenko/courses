// C++ API: Результат паросполучення
namespace net {

struct MatchingResult {
    std::size_t matching_size{0};
    std::vector<int> match_left;  // Індекси вершин V (-1 якщо вільна)
    std::vector<int> match_right; // Індекси вершин U (-1 якщо вільна)
    std::vector<std::size_t> vertex_cover; // Вершини покриття C
    std::size_t cover_size{0};
};

} // namespace net
