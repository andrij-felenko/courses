#include <vector>
#include <memory>

class PlanarGraphModel {
public:
    explicit PlanarGraphModel(std::size_t num_vertices, std::size_t max_edges = 0);
    ~PlanarGraphModel() = default;

    PlanarGraphModel(const PlanarGraphModel&) = delete;
    PlanarGraphModel& operator=(const PlanarGraphModel&) = delete;
    PlanarGraphModel(PlanarGraphModel&&) noexcept = default;
    PlanarGraphModel& operator=(PlanarGraphModel&&) noexcept = default;

    [[nodiscard]] std::size_t vertex_count() const noexcept { return num_vertices_; }
    [[nodiscard]] std::size_t edge_count() const noexcept { return num_edges_; }
    [[nodiscard]] std::size_t face_count() const noexcept { return faces_.size(); }
    [[nodiscard]] bool is_embedded() const noexcept { return is_embedded_; }

private:
    std::size_t num_vertices_{0};
    std::size_t num_edges_{0};
    bool is_embedded_{false};

    std::vector<HalfEdgeRecord> half_edges_;
    std::vector<std::vector<std::size_t>> rotation_system_;
    std::vector<FaceRecord> faces_;
};
