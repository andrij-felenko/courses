#pragma once

#include <vector>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <span>

namespace graph::analytics {

enum class AlgorithmMode {
    ScalarWarshall,
    BitsetVectorized,
    SparseDFS
};

struct EngineConfig {
    size_t vertices;
    AlgorithmMode mode{AlgorithmMode::BitsetVectorized};
    bool auto_reflexive{false};
};

enum class Status {
    Success = 0,
    NullPointer = -1,
    InvalidVertex = -2,
    NoMemory = -3,
    Frozen = -4,
    NotComputed = -5
};

class ReachabilityEngine {
public:
    explicit ReachabilityEngine(const EngineConfig& config);
    ~ReachabilityEngine() noexcept;

    ReachabilityEngine(const ReachabilityEngine&) = delete;
    ReachabilityEngine& operator=(const ReachabilityEngine&) = delete;

    ReachabilityEngine(ReachabilityEngine&&) noexcept;
    ReachabilityEngine& operator=(ReachabilityEngine&&) noexcept;

    void addEdge(size_t u, size_t v);
    void compute();
    [[nodiscard]] bool isReachable(size_t u, size_t v) const;
    [[nodiscard]] std::vector<size_t> getReachableSet(size_t u) const;
    [[nodiscard]] size_t vertexCount() const noexcept;
    [[nodiscard]] bool isComputed() const noexcept;

private:
    class Impl;
    Impl* impl_;
};

} // namespace graph::analytics
