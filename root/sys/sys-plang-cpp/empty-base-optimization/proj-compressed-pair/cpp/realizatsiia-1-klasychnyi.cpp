#include <type_traits>
#include <utility>
#include <tuple>
#include <memory>
#include <cstddef>

namespace legacy {

// Метафункція: перевіряє, чи можна застосувати EBO до конкретного типу
template <typename T>
constexpr bool can_apply_ebo_v = std::is_empty_v<T> && !std::is_final_v<T>;

// Базовий шаблон елемента пари з дискримінатором індексу
template <typename T, size_t Index, bool CanEbo = can_apply_ebo_v<T>>
class compressed_pair_element;

// Спеціалізація 1: Звичайне збереження в полі.
// Застосовується, якщо тип містить дані, є скаляром або позначений як final.
template <typename T, size_t Index>
class compressed_pair_element<T, Index, false> {
    T value_{};

public:
    compressed_pair_element() = default;

    template <typename U>
    explicit constexpr compressed_pair_element(U&& val)
        : value_(std::forward<U>(val)) {}

    template <typename... Args, size_t... Indices>
    constexpr compressed_pair_element(std::piecewise_construct_t,
                                      std::tuple<Args...> args,
                                      std::index_sequence<Indices...>)
        : value_(std::get<Indices>(std::move(args))...) {}

    constexpr T& get() noexcept { return value_; }
    constexpr const T& get() const noexcept { return value_; }
};

// Спеціалізація 2: Оптимізація порожньої бази через приватне спадкування.
// Застосовується виключно для порожніх класів, які дозволяють спадкування.
template <typename T, size_t Index>
class compressed_pair_element<T, Index, true> : private T {
public:
    compressed_pair_element() = default;

    template <typename U>
    explicit constexpr compressed_pair_element(U&& val)
        : T(std::forward<U>(val)) {}

    template <typename... Args, size_t... Indices>
    constexpr compressed_pair_element(std::piecewise_construct_t,
                                      std::tuple<Args...> args,
                                      std::index_sequence<Indices...>)
        : T(std::get<Indices>(std::move(args))...) {}

    constexpr T& get() noexcept { return *this; }
    constexpr const T& get() const noexcept { return *this; }
};

// Головний контейнерний клас стисненої пари
template <typename T1, typename T2>
class compressed_pair : private compressed_pair_element<T1, 0>,
                        private compressed_pair_element<T2, 1> {
    using FirstBase = compressed_pair_element<T1, 0>;
    using SecondBase = compressed_pair_element<T2, 1>;

public:
    compressed_pair() = default;

    template <typename U1, typename U2>
    constexpr compressed_pair(U1&& first_arg, U2&& second_arg)
        : FirstBase(std::forward<U1>(first_arg)),
          SecondBase(std::forward<U2>(second_arg)) {}

    template <typename... Args1, typename... Args2>
    constexpr compressed_pair(std::piecewise_construct_t pw,
                              std::tuple<Args1...> first_args,
                              std::tuple<Args2...> second_args)
        : FirstBase(pw, std::move(first_args), std::index_sequence_for<Args1...>{}),
          SecondBase(pw, std::move(second_args), std::index_sequence_for<Args2...>{}) {}

    constexpr T1& first() noexcept { return FirstBase::get(); }
    constexpr const T1& first() const noexcept { return FirstBase::get(); }

    constexpr T2& second() noexcept { return SecondBase::get(); }
    constexpr const T2& second() const noexcept { return SecondBase::get(); }
};

} // namespace legacy
