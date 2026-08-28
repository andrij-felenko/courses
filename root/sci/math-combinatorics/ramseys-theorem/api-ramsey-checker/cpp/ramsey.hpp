// ramsey.hpp - C++20 Modern Object-Oriented API Interface
#ifndef LIBRAMSEY_HPP
#define LIBRAMSEY_HPP

#include <vector>
#include <optional>
#include <string_view>
#include <system_error>
#include <cstdint>
#include <span>
#include <filesystem>
#include <chrono>

namespace ramsey {

enum class error_code {
    invalid_argument = 1,
    out_of_memory,
    search_timeout,
    file_io_error
};

class graph_color_matrix {
public:
    explicit graph_color_matrix(std::size_t num_vertices);
    ~graph_color_matrix() = default;

    graph_color_matrix(const graph_color_matrix&) = default;
    graph_color_matrix& operator=(const graph_color_matrix&) = default;
    graph_color_matrix(graph_color_matrix&&) noexcept = default;
    graph_color_matrix& operator=(graph_color_matrix&&) noexcept = default;

    [[nodiscard]] std::size_t vertices_count() const noexcept;
    
    void set_edge(std::size_t u, std::size_t v, bool is_red);
    [[nodiscard]] bool is_red_edge(std::size_t u, std::size_t v) const;

    [[nodiscard]] std::uint64_t get_row_mask(std::size_t v) const;

    void export_json(const std::filesystem::path& path) const;
    static graph_color_matrix import_json(const std::filesystem::path& path);

private:
    std::size_t num_vertices_;
    std::vector<std::uint64_t> adj_matrix_;
};

struct clique_search_result {
    bool has_monochromatic_clique{false};
    std::size_t clique_size{0};
    bool is_red{false};
    std::vector<std::size_t> clique_vertices;
};

class ramsey_analyzer {
public:
    explicit ramsey_analyzer(std::size_t r, std::size_t s);

    [[nodiscard]] clique_search_result analyze(const graph_color_matrix& graph) const;
    
    [[nodiscard]] std::optional<graph_color_matrix> find_counterexample(
        std::size_t num_vertices, 
        std::chrono::seconds timeout = std::chrono::seconds(60)
    ) const;

private:
    std::size_t r_;
    std::size_t s_;
};

} // namespace ramsey

#endif // LIBRAMSEY_HPP
