// compat/serialize_feature.hpp
#pragma once

#include <type_traits>
#include <cstring>
#include <vector>
#include <cstdint>

#include "version_check.hpp"

namespace compat {

#if defined(__cpp_concepts) && (__cpp_concepts >= 201907L)

    // Сучасна гілка C++20: декларативні концепти та клаузула requires
    template <typename T>
    concept TriviallyCopyable = std::is_trivially_copyable_v<T>;

    template <typename T>
    concept CustomSerializable = requires(const T& obj, std::vector<uint8_t>& buf) {
        obj.write_custom(buf);
    };

    // Перевантаження для тривіальних типів (висока продуктивність)
    template <TriviallyCopyable T>
    void serialize(const T& value, std::vector<uint8_t>& buffer) {
        const auto* byte_ptr = reinterpret_cast<const uint8_t*>(&value);
        buffer.insert(buffer.end(), byte_ptr, byte_ptr + sizeof(T));
    }

    // Перевантаження для користувацьких типів з методом write_custom
    template <CustomSerializable T>
        requires (!TriviallyCopyable<T>)
    void serialize(const T& value, std::vector<uint8_t>& buffer) {
        value.write_custom(buffer);
    }

#else

    // Запасна гілка C++14/C++17: метапрограмування SFINAE через std::enable_if_t
    template <typename T, std::enable_if_t<std::is_trivially_copyable<T>::value, int> = 0>
    void serialize(const T& value, std::vector<uint8_t>& buffer) {
        const auto* byte_ptr = reinterpret_cast<const uint8_t*>(&value);
        buffer.insert(buffer.end(), byte_ptr, byte_ptr + sizeof(T));
    }

    template <typename T, std::enable_if_t<!std::is_trivially_copyable<T>::value, int> = 0>
    void serialize(const T& value, std::vector<uint8_t>& buffer) {
        value.write_custom(buffer);
    }

#endif

} // namespace compat
