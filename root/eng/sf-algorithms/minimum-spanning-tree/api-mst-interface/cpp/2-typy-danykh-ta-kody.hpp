#pragma once

#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <expected>

namespace mst {

enum class StatusCode : int32_t {
    Success = 0,
    DisconnectedGraph = 1,
    InvalidArgument = 2,
    VertexOutOfBounds = 3,
    OutOfMemory = 4
};

enum class AlgorithmType : int32_t {
    Auto = 0,
    Prim = 1,
    Boruvka = 2
};

struct EdgeDesc {
    int32_t u{0};
    int32_t v{0};
    int64_t weight{0};
};

struct Solution {
    std::vector<EdgeDesc> edges;
    int64_t total_weight{0};
    size_t num_components{0};
    StatusCode status{StatusCode::Success};

    [[nodiscard]] bool is_connected_tree() const noexcept {
        return num_components <= 1 && status == StatusCode::Success;
    }
};

} // namespace mst
