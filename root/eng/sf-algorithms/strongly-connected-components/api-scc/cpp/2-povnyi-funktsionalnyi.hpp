namespace scc {

enum class ErrorCode {
    InvalidVertexIndex = 1,
    NullPointerArgument,
    CyclicDependencyInDAG,
    AllocationFailure
};

class SCCAnalyzer {
public:
    explicit SCCAnalyzer(int num_vertices, AnalyzerConfig config = {});

    /* Додавання орієнтованого ребра u -> v */
    void add_edge(int from, int to);

    /* Масове встановлення сусідів для вершини u */
    void set_neighbors(int u, std::span<const int> neighbors);

    /* Перевірка валідності індексу вершини */
    [[nodiscard]] bool is_valid_vertex(int v) const noexcept;

    /* Обчислення компонент та побудова DAG конденсації */
    [[nodiscard]] std::expected<AnalysisResult, ErrorCode> analyze() const;

    /* Серіалізація результатів у формат Graphviz DOT */
    [[nodiscard]] std::string to_dot(const AnalysisResult& result) const;

    /* Серіалізація результатів у формат JSON */
    [[nodiscard]] std::string to_json(const AnalysisResult& result) const;
};

} // namespace scc
