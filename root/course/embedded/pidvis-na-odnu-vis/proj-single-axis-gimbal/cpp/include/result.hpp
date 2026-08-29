// result.hpp — результат операції з кодом помилки замість -1 та errno.
//
// На AVR прошивку збирають із -fno-exceptions, а <expected> у freestanding
// libstdc++ немає. Тому тут мінімальний Result: він робить рівно те, чого
// ми хочемо від std::expected, — не дає взяти значення, не спитавши про
// успіх, і не дає мовчки проігнорувати помилку ([[nodiscard]]).

#pragma once

#include <cstdint>
#include <utility>

namespace gimbal {

template <typename T, typename E>
class [[nodiscard]] Result {
public:
    static constexpr Result ok(T value) noexcept {
        return Result{std::move(value), E{}, true};
    }
    static constexpr Result fail(E error) noexcept {
        return Result{T{}, error, false};
    }

    constexpr explicit operator bool() const noexcept { return ok_; }

    // Кликати тільки після перевірки: в іншому разі повернеться порожнє T{},
    // і це навмисно помітно в телеметрії, а не тихо, як у випадку з -1.
    constexpr const T& value() const noexcept { return value_; }
    constexpr E error() const noexcept { return error_; }

private:
    constexpr Result(T value, E error, bool ok) noexcept
        : value_{std::move(value)}, error_{error}, ok_{ok} {}

    // Тримаємо обидва поля поруч, без union: T тут — тривіальні структури
    // на десяток байтів, і чесна проста розкладка коштує менше за
    // ручне керування часом життя в об'єднанні.
    T    value_;
    E    error_;
    bool ok_;
};

// Спеціалізація для операцій без результату: «записав регістр» повертає
// або згоду, або причину відмови.
template <typename E>
class [[nodiscard]] Result<void, E> {
public:
    static constexpr Result ok() noexcept { return Result{E{}, true}; }
    static constexpr Result fail(E error) noexcept { return Result{error, false}; }

    constexpr explicit operator bool() const noexcept { return ok_; }
    constexpr E error() const noexcept { return error_; }

private:
    constexpr Result(E error, bool ok) noexcept : error_{error}, ok_{ok} {}

    E    error_;
    bool ok_;
};

}  // namespace gimbal
