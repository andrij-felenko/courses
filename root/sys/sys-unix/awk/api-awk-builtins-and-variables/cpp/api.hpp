// api.hpp — типобезпечна обгортка над <gawkapi.h>.
//
// Сирий API — це C: аргумент беруть за номером, рядок приходить парою
// (вказівник, довжина) без нуля в кінці, а помилку повертають нулем. Тут це
// один раз загорнуто в std::optional і std::string_view, щоб самі функції
// розширення читалися як звичайний C++, а не як розбір чужого протоколу.
//
// <gawkapi.h> сам загортає себе в extern "C" для C++, тож підключаємо його
// звичайно; зайва обгортка тут лише зіпсувала б включені ним заголовки.
#pragma once

#include <gawkapi.h>

#include <cerrno>
#include <cstddef>
#include <cstring>
#include <optional>
#include <string_view>

// Макроси <gawkapi.h> розгортаються у звернення до ЦИХ двох імен, тому вони
// зобов'язані бути видимі в кожному файлі модуля. Визначені один раз — в
// extension.cpp. У C-варіанті з однієї одиниці трансляції вони були static;
// щойно файлів стало більше, так уже не можна.
extern const gawk_api_t *api;
extern awk_ext_id_t ext_id;

namespace fast_tools::glue {

// Рядок AWK — пара (байти, довжина), і термінального нуля контракт не
// обіцяє. string_view — точний відповідник цієї пари; std::string був би
// зайвою копією, а strlen() над .str — класичною помилкою розширень.
[[nodiscard]] inline std::optional<std::string_view>
string_arg(int nargs, int index) noexcept
{
    if (index < 0 || index >= nargs)
        return std::nullopt;

    awk_value_t value{};
    if (!get_argument(index, AWK_STRING, &value))
        return std::nullopt;
    if (value.str_value.str == nullptr)
        return std::string_view{};

    return std::string_view(value.str_value.str, value.str_value.len);
}

[[nodiscard]] inline std::optional<double>
number_arg(int nargs, int index) noexcept
{
    if (index < 0 || index >= nargs)
        return std::nullopt;

    awk_value_t value{};
    if (!get_argument(index, AWK_NUMBER, &value))
        return std::nullopt;

    return value.num_value;
}

// Помилка розширення — не привід валити інтерпретатор. fatal() убив би весь
// скрипт разом із блоком END; ERRNO лишає рішення за програмою на AWK.
inline awk_value_t *fail(const char *message, awk_value_t *result) noexcept
{
    update_ERRNO_string(message);
    return make_null_string(result);
}

inline awk_value_t *fail_errno(int code, awk_value_t *result) noexcept
{
    update_ERRNO_int(code);          // сам перекладе код у strerror(3)
    return make_null_string(result);
}

// Успіх мусить прибирати за собою: інакше скрипт побачить ERRNO від чужого
// невдалого виклику й вирішить, що зламалися саме ми.
inline void clear_errno() noexcept
{
    unset_ERRNO();
}

// Рядок переходить у власність gawk, і звільнить його ВІН — своїм free().
// Тому буфер мусить бути з gawk_malloc(): ні std::string, ні new сюди не
// годяться, це не наша пам'ять і не наш аллокатор.
inline awk_value_t *give_string(std::string_view text, awk_value_t *result) noexcept
{
    auto *buffer = static_cast<char *>(gawk_malloc(text.size() + 1));
    if (buffer == nullptr)
        return fail_errno(ENOMEM, result);

    // memcpy з nullptr — невизначена поведінка навіть за нульової довжини,
    // а порожній string_view цілком законно має data() == nullptr.
    if (!text.empty())
        std::memcpy(buffer, text.data(), text.size());
    buffer[text.size()] = '\0';

    return make_malloced_string(buffer, text.size(), result);
}

// Найчастіша помилка заповнення таблиці функцій — переставлені місцями max і
// min: компілятор мовчить, а gawk починає вимагати аргументів більше, ніж
// функція взагалі здатна прийняти.
[[nodiscard]] inline bool descriptor_is_sane(const awk_ext_func_t &f) noexcept
{
    return f.name != nullptr
        && f.name[0] != '\0'
        && f.function != nullptr
        && f.min_required_args <= f.max_expected_args;
}

} // namespace fast_tools::glue
