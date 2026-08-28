#include <string_view>
#include <atomic>
#include <cstdint>

struct SubsystemNode {
    std::string_view name;
    uint32_t priority;
    void (*initialize_fn)();
    SubsystemNode* next{nullptr};

    // constexpr-конструктор дозволяє сформувати структуру вузла під час збірки
    constexpr SubsystemNode(std::string_view n, uint32_t p, void (*init)()) noexcept
        : name(n), priority(p), initialize_fn(init), next(nullptr) {}
};
