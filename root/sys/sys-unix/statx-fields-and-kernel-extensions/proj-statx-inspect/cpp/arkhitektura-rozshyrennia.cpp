#include <concepts>
#include <system_error>

template <typename T>
concept StatxFieldFetcher = requires(T a, std::string_view path) {
    { a.fetch_field(path) } -> std::same_as<void>;
};

// Приклад типобезпечного обгортання маскового запиту
enum class StatxMaskBit : uint32_t {
    Basic = STATX_BASIC_STATS,
    BirthTime = STATX_BTIME,
#ifdef STATX_DIOALIGN
    DirectIO = STATX_DIOALIGN,
#endif
};

constexpr inline StatxMaskBit operator|(StatxMaskBit a, StatxMaskBit b) noexcept {
    return static_cast<StatxMaskBit>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}
