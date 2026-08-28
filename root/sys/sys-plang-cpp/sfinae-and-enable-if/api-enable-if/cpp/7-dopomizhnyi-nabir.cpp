#include <experimental/type_traits>

// 1. Оголошення мета-виразу
template<typename T>
using serialize_op = decltype(std::declval<T>().serialize());

// 2. Предикат існування
template<typename T>
using has_serialize = std::experimental::is_detected<serialize_op, T>;

// 3. Отримання результуючого типу або заглушки
template<typename T>
using serialize_result_t = std::experimental::detected_or_t<void, serialize_op, T>;
