#include <concepts>

template<typename T>
concept HashableScalar = std::integral<T> && !std::same_as<T, bool>;

// Застосування концепту в заголовку шаблону
template<HashableScalar T>
T compute_hash(T value) {
    return value ^ 0x9e3779b9;
}
