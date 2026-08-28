#include <iostream>
#include <vector>
#include <cstdint>
#include <limits>
#include <span>
#include <optional>
#include <algorithm>

using Entity = std::uint32_t;
inline constexpr Entity kInvalidEntity = std::numeric_limits<Entity>::max();
inline constexpr std::uint32_t kInvalidIndex = std::numeric_limits<std::uint32_t>::max();

struct Position {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct Velocity {
    float vx{0.0f};
    float vy{0.0f};
    float vz{0.0f};
};

template <typename TComponent>
class ComponentPool {
public:
    explicit ComponentPool(std::size_t max_entities = 100'000)
        : sparse_(max_entities, kInvalidIndex) {}

    [[nodiscard]] bool has(Entity e) const noexcept {
        return e < sparse_.size() && sparse_[e] != kInvalidIndex;
    }

    void add(Entity e, TComponent comp) {
        if (e >= sparse_.size()) {
            sparse_.resize(std::max(sparse_.size() * 2, static_cast<std::size_t>(e + 1)), kInvalidIndex);
        }
        if (has(e)) {
            data_[sparse_[e]] = comp;
            return;
        }

        const auto idx = static_cast<std::uint32_t>(dense_entities_.size());
        dense_entities_.push_back(e);
        data_.push_back(comp);
        sparse_[e] = idx;
    }

    bool remove(Entity e) noexcept {
        if (!has(e)) {
            return false;
        }

        const std::uint32_t removed_idx = sparse_[e];
        const std::uint32_t last_idx = static_cast<std::uint32_t>(dense_entities_.size() - 1);

        if (removed_idx != last_idx) {
            const Entity last_entity = dense_entities_[last_idx];
            dense_entities_[removed_idx] = last_entity;
            data_[removed_idx] = std::move(data_[last_idx]);
            sparse_[last_entity] = removed_idx;
        }

        sparse_[e] = kInvalidIndex;
        dense_entities_.pop_back();
        data_.pop_back();
        return true;
    }

    [[nodiscard]] TComponent* get(Entity e) noexcept {
        if (!has(e)) return nullptr;
        return &data_[sparse_[e]];
    }

    [[nodiscard]] std::span<TComponent> data() noexcept {
        return data_;
    }

    [[nodiscard]] std::span<const TComponent> data() const noexcept {
        return data_;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return data_.size();
    }

private:
    std::vector<std::uint32_t> sparse_;
    std::vector<Entity>        dense_entities_;
    std::vector<TComponent>    data_;
};

// Система руху, що оперує безпосередньо неперервними зрізами пам'яті
void update_movement(std::span<Position> positions, std::span<const Velocity> velocities, float dt) noexcept {
    const std::size_t n = std::min(positions.size(), velocities.size());
    for (std::size_t i = 0; i < n; ++i) {
        positions[i].x += velocities[i].vx * dt;
        positions[i].y += velocities[i].vy * dt;
        positions[i].z += velocities[i].vz * dt;
    }
}
