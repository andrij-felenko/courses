// Концептуальне відображення меж середовища у просторі пам'яті процесу
#include <cstdint>
#include <span>

struct ProcessMemoryBounds {
    std::uintptr_t arg_start{0};
    std::uintptr_t arg_end{0};
    std::uintptr_t env_start{0};
    std::uintptr_t env_end{0};

    [[nodiscard]] std::size_t environment_size() const noexcept {
        return (env_end >= env_start) ? (env_end - env_start) : 0;
    }
};
