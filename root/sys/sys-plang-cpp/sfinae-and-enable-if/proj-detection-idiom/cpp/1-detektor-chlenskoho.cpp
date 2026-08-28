#include <type_traits>
#include <utility>
#include <vector>
#include <string>
#include <iostream>
#include <cstring>
#include <cstdint>

using Buffer = std::vector<uint8_t>;

// 1. Первинний шаблон: за замовчуванням метод відсутній
template<typename T, typename = void>
struct has_member_serialize : std::false_type {};

// 2. Часткова спеціалізація для валідного виразу
template<typename T>
struct has_member_serialize<T, std::void_t<
    decltype(std::declval<const T&>().serialize(std::declval<Buffer&>()))
>> : std::true_type {};

template<typename T>
inline constexpr bool has_member_serialize_v = has_member_serialize<T>::value;
