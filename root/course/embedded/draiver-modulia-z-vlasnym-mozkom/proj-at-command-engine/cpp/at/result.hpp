#pragma once

#include <cstdint>
#include <expected>
#include <string_view>

namespace at {

/* Успіх і відмова не змішуються в одному enum: успіх — це значення
   (змістовний рядок відповіді, можливо порожній), відмова — це Failure.
   Прикладний код не може випадково прочитати «дані» там, де їх немає. */
enum class Status : std::uint8_t {
    Error,    // модуль відповів ERROR / +CME ERROR / +CMS ERROR
    Timeout,  // модуль промовчав
    Aborted,  // чергу скасовано під час аварійного відновлення
};

[[nodiscard]] constexpr std::string_view to_string(Status status) noexcept
{
    switch (status) {
        case Status::Error:   return "ERROR";
        case Status::Timeout: return "TIMEOUT";
        case Status::Aborted: return "ABORTED";
    }
    return "?";
}

struct Failure {
    Status status{Status::Error};
    /* Текст, який прислав модуль. Дивиться у внутрішній буфер рядка й дійсний
       ЛИШЕ на час виклику колбека — кому треба довше, копіює. */
    std::string_view detail{};
};

using Result = std::expected<std::string_view, Failure>;

}  // namespace at
