#include "builtins.hpp"

#include <chrono>
#include <string_view>

#include "api.hpp"
#include "fnv1a.hpp"

namespace fast_tools {

awk_value_t *monotonic_time_ns(int, awk_value_t *result, struct awk_ext_func *) noexcept
{
    // steady_clock і Є монотонним годинником: на Linux це CLOCK_MONOTONIC,
    // якого стрибки NTP не смикають. Перевіряємо це вимогою, а не вірою.
    static_assert(std::chrono::steady_clock::is_steady,
                  "steady_clock на цій платформі не монотонний — беріть clock_gettime");

    const auto since_start = std::chrono::steady_clock::now().time_since_epoch();
    const auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(since_start).count();

    // duration_cast знімає питання одиниць назавжди: у C ту саму роботу
    // робило множення tv_sec на 1e9, і саме там помилялися.
    //
    // AWK бачить лише double — 53 біти мантиси. Наносекунди лишаються
    // точними до цілого приблизно 104 доби від початку відліку: для
    // вимірювання ІНТЕРВАЛІВ цього досить, для абсолютних міток уже ні.
    glue::clear_errno();
    return make_number(static_cast<double>(ns), result);
}

awk_value_t *fnv1a_64_of_string(int nargs, awk_value_t *result, struct awk_ext_func *) noexcept
{
    const auto input = glue::string_arg(nargs, 0);
    if (!input)
        return glue::fail("fnv1a_64: очікується один рядковий аргумент", result);

    // Ані хеш, ані його форматування нічого не виділяють: to_hex повертає
    // масив на стеку. Єдина алокація за виклик — та, що переходить gawk.
    const auto hex = to_hex(fnv1a_64(*input));

    glue::clear_errno();
    return glue::give_string(std::string_view(hex.data(), hex.size()), result);
}

} // namespace fast_tools
