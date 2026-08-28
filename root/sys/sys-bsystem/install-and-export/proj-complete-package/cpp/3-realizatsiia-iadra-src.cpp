#include "hyperion/core.hpp"

namespace hyperion {

Engine::Engine(std::string name)
    : name_(std::move(name)) {}

std::string_view Engine::name() const noexcept {
    return name_;
}

uint32_t Engine::compute_hash(std::string_view payload) const noexcept {
    // Алгоритм 32-бітного хешування FNV-1a
    uint32_t hash = 2166136261u;
    for (char c : payload) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 16777619u;
    }
    return hash;
}

} // namespace hyperion
