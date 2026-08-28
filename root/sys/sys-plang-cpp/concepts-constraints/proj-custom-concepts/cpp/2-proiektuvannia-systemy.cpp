#include <concepts>
#include <ranges>
#include <span>
#include <cstddef>
#include <cstring>
#include <vector>
#include <string>
#include <string_view>
#include <type_traits>
#include <iostream>
#include <memory>
#include <cstdint>
#include <bit>
#include <stdexcept>
#include <algorithm>

// 1. Концепт вихідного бінарного потоку
template<typename S>
concept ByteStream = requires(S& stream, std::span<const std::byte> bytes) {
    { stream.write(bytes) } -> std::same_as<std::size_t>;
};

// 2. Концепт вхідного бінарного джерела для десеріалізації
template<typename S>
concept ByteSource = requires(S& source, std::span<std::byte> dest) {
    { source.read(dest) } -> std::same_as<std::size_t>;
};

// 3. Концепт тривіально копійовних типів (без вказівників та діапазонів)
template<typename T>
concept TriviallySerializable = 
    std::is_trivially_copyable_v<T> &&
    !std::is_pointer_v<T> &&
    !std::is_null_pointer_v<T> &&
    !std::ranges::range<T>;

// 4. Концепт об'єктів із власним методом серіалізації
template<typename T, typename Stream>
concept CustomSerializable = requires(const T& obj, Stream& stream) {
    requires ByteStream<Stream>;
    { obj.serialize(stream) } -> std::same_as<void>;
};

// 5. Концепт об'єктів із власним методом десеріалізації
template<typename T, typename Source>
concept CustomDeserializable = requires(T& obj, Source& source) {
    requires ByteSource<Source>;
    { obj.deserialize(source) } -> std::same_as<void>;
};

// 6. Концепт рядкових типів (неперервний масив символів char / char8_t)
template<typename T>
concept StringLike = 
    std::ranges::contiguous_range<T> &&
    std::ranges::sized_range<T> &&
    (std::same_as<std::ranges::range_value_t<T>, char> ||
     std::same_as<std::ranges::range_value_t<T>, char8_t>);

// 7. Концепт неперервного діапазону тривіальних типів для прямого блокового копіювання
template<typename T>
concept TriviallyContiguousRange = 
    std::ranges::contiguous_range<T> &&
    std::ranges::sized_range<T> &&
    TriviallySerializable<std::ranges::range_value_t<T>> &&
    !StringLike<T>;

// 8. Концепт узагальненого діапазону (виключаючи рядки та тривіальні неперервні масиви)
template<typename T>
concept SerializableRange = 
    std::ranges::input_range<T> &&
    std::ranges::sized_range<T> &&
    !StringLike<T> &&
    !TriviallyContiguousRange<T>;

// 9. Концепт змінюваного контейнера для десеріалізації
template<typename T>
concept DeserializableContainer = 
    std::ranges::range<T> &&
    requires(T& container) {
        container.clear();
        container.emplace_back(std::declval<std::ranges::range_value_t<T>>());
    };
