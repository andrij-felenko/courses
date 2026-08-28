// Шаблонна утиліта безпечного читання багатобайтних чисел з gsl::span
template <class T, std::ptrdiff_t Offset>
[[nodiscard]] constexpr T read_big_endian(gsl::span<const gsl::byte> data) noexcept {
    static_assert(std::is_trivially_copyable_v<T>, "T must be trivially copyable");
    T value{};
    auto slice = data.template subspan<Offset, sizeof(T)>();
    std::memcpy(&value, slice.data(), sizeof(T));

    // У реальному C++23 застосовуємо std::byteswap, для C++17/20 — бітові зсуви або ntoh
    if constexpr (sizeof(T) == 2) {
        auto raw = static_cast<uint16_t>(value);
        return static_cast<T>((raw >> 8) | (raw << 8));
    } else if constexpr (sizeof(T) == 4) {
        auto raw = static_cast<uint32_t>(value);
        return static_cast<T>(((raw >> 24) & 0xFF) |
                              ((raw >> 8)  & 0xFF00) |
                              ((raw << 8)  & 0xFF0000) |
                              ((raw << 24) & 0xFF000000));
    }
    return value;
}
