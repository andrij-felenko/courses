#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <cstdint>
#include <algorithm>
#include <limits>

namespace cellular {

enum class CellState {
    Inactive = 0,
    Active = 1,
    Draining = 2,
    Unhealthy = 3
};

struct CellDescriptor {
    uint32_t id;
    std::string endpoint;
    CellState state{CellState::Active};
    uint32_t active_connections{0};
};

class CellRouter {
public:
    explicit CellRouter(size_t shuffle_k = 3) : shuffle_k_(shuffle_k) {}

    bool add_cell(uint32_t id, std::string endpoint, CellState state = CellState::Active) {
        cells_.push_back(CellDescriptor{id, std::move(endpoint), state, 0});
        return true;
    }

    void set_cell_state(uint32_t cell_id, CellState new_state) {
        for (auto &cell : cells_) {
            if (cell.id == cell_id) {
                cell.state = new_state;
                break;
            }
        }
    }

    /* 1. Пряма маршрутизація: обрання активної комірки за хешем */
    [[nodiscard]] std::optional<CellDescriptor> route_direct(std::string_view tenant_id) const {
        if (cells_.empty()) {
            return std::nullopt;
        }
        const uint64_t hash = hash_fnv1a(tenant_id);
        const size_t start_idx = hash % cells_.size();

        for (size_t i = 0; i < cells_.size(); ++i) {
            const size_t idx = (start_idx + i) % cells_.size();
            if (cells_[idx].state == CellState::Active) {
                return cells_[idx];
            }
        }
        return std::nullopt;
    }

    /* 2. Перемішане шардування (Shuffle Sharding): вибір з K ізольованих комірок */
    [[nodiscard]] std::optional<CellDescriptor> route_shuffle(std::string_view tenant_id) const {
        if (cells_.empty()) {
            return std::nullopt;
        }
        const size_t k = std::min(shuffle_k_, cells_.size());
        const auto candidate_indices = compute_shuffle_subset(tenant_id, k);

        const CellDescriptor *best = nullptr;
        uint32_t min_load = std::numeric_limits<uint32_t>::max();

        for (const size_t idx : candidate_indices) {
            const auto &cell = cells_[idx];
            if (cell.state == CellState::Active) {
                if (cell.active_connections < min_load) {
                    min_load = cell.active_connections;
                    best = &cell;
                }
            }
        }

        if (best != nullptr) {
            return *best;
        }
        return std::nullopt;
    }

private:
    std::vector<CellDescriptor> cells_;
    size_t shuffle_k_{3};

    static uint64_t hash_fnv1a(std::string_view str) noexcept {
        uint64_t hash = 14695981039346656037ULL;
        for (const char c : str) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 1099511628211ULL;
        }
        return hash;
    }

    [[nodiscard]] std::vector<size_t> compute_shuffle_subset(std::string_view key, size_t k) const {
        std::vector<size_t> subset;
        subset.reserve(k);
        uint64_t state = hash_fnv1a(key);

        while (subset.size() < k) {
            state = state * 6364136223846793005ULL + 1442695040888963407ULL;
            const size_t candidate = (state >> 32) % cells_.size();
            if (std::find(subset.begin(), subset.end(), candidate) == subset.end()) {
                subset.push_back(candidate);
            }
        }
        return subset;
    }
};

} // namespace cellular
