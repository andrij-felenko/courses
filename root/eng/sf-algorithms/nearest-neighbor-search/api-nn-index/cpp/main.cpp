#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>
#include <memory>
#include <expected>
#include <chrono>

enum class MetricType {
    L2 = 0,
    Cosine = 1,
    InnerProduct = 2
};

enum class EngineType {
    FlatScan = 0,
    MetricTree = 1,
    GraphHNSW = 2,
    QuantizedIVF = 3
};

enum class IndexError {
    InvalidArgument = 1,
    OutOfMemory = 2,
    DimensionMismatch = 3,
    IndexNotBuilt = 4,
    ConcurrencyViolation = 5
};

struct IndexConfig {
    int dimension{128};
    MetricType metric{MetricType::L2};
    EngineType engine{EngineType::FlatScan};
    size_t initial_capacity{10000};
    float approximation_factor{0.0f};
    int num_threads{0};
};

struct SearchStats {
    size_t distance_evaluations{0};
    size_t nodes_visited{0};
    std::chrono::nanoseconds latency{0};
    float recall_estimate{1.0f};
};

struct SearchResult {
    std::vector<int64_t> ids;
    std::vector<float> distances;
    SearchStats stats;
};

class INearestNeighborIndex {
public:
    virtual ~INearestNeighborIndex() = default;

    [[nodiscard]] virtual int dimension() const noexcept = 0;
    [[nodiscard]] virtual size_t size() const noexcept = 0;
    [[nodiscard]] virtual MetricType metric() const noexcept = 0;

    virtual std::expected<void, IndexError> build(
        std::span<const float> raw_vectors,
        std::span<const int64_t> ids) = 0;

    virtual std::expected<void, IndexError> insert(
        int64_t id,
        std::span<const float> vector) = 0;

    [[nodiscard]] virtual std::expected<SearchResult, IndexError> search_knn(
        std::span<const float> query,
        size_t k) const = 0;

    [[nodiscard]] virtual std::expected<SearchResult, IndexError> search_radius(
        std::span<const float> query,
        float radius) const = 0;
};
