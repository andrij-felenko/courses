// --- C++20 Публічний заголовок lsh_index.hpp ---

#pragma once
#include <vector>
#include <span >
#include <expected>
#include <cstdint>
#include <memory>

namespace net::lsh {

enum class Metric {
    Jaccard,
    Cosine,
    Euclidean
};

enum class ErrorCode {
    InvalidArgument,
    OutOfMemory,
    DimensionMismatch,
    IndexEmpty
};

struct Config {
    Metric metric = Metric::Cosine;
    size_t dim = 128;
    size_t num_bands = 20;
    size_t rows_per_band = 5;
    float  bin_width = 4.0f;
    uint32_t seed = 1337;
};

struct Match {
    uint64_t id;
    float distance;
};

template <typename T = float>
class Index {
public:
    static std::expected<std::unique_ptr<Index<T>>, ErrorCode> create(const Config& config);

    virtual ~Index() = default;

    [[nodiscard]] virtual std::expected<void, ErrorCode> insert(
        uint64_t id,
        std::span<const T> vector
    ) = 0;

    [[nodiscard]] virtual std::expected<std::vector<Match>, ErrorCode> query_knn(
        std::span<const T> query_vector,
        size_t top_k,
        size_t max_candidates = 0
    ) const = 0;

    [[nodiscard]] virtual size_t size() const noexcept = 0;
    [[nodiscard]] virtual size_t memory_usage_bytes() const noexcept = 0;
};

} // namespace net::lsh
