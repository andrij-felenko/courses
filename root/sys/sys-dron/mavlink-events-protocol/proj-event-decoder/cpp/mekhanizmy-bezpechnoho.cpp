#include <cstdint>
#include <cstring>
#include <span>
#include <bit>
#include <type_traits>

// Універсальний розпакувальник скалярних типів (C++20)
template <typename T>
T unpackArgLE(std::span<const uint8_t> buf, size_t offset) noexcept {
    static_assert(std::is_trivially_copyable_v<T>, "Тип аргументу має бути тривіально копійованим");
    T val{};
    if (offset + sizeof(T) <= buf.size()) {
        std::memcpy(&val, buf.data() + offset, sizeof(T));
    }
    return val;
}

inline uint8_t unpackU8(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<uint8_t>(buf, offset);
}

inline uint16_t unpackU16LE(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<uint16_t>(buf, offset);
}

inline uint32_t unpackU32LE(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<uint32_t>(buf, offset);
}

inline float unpackF32LE(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<float>(buf, offset);
}

inline uint64_t unpackU64LE(std::span<const uint8_t> buf, size_t offset) noexcept {
    return unpackArgLE<uint64_t>(buf, offset);
}
