#pragma once

#include <cstddef>
#include <cstdint>
#include <span>

#include "at/config.hpp"
#include "at/inplace_function.hpp"
#include "at/result.hpp"
#include "at/static_string.hpp"

namespace at {

using DoneCallback = InplaceFunction<void(const Result&), config::kCallbackStorage>;
using UrcHandler = InplaceFunction<void(std::string_view), config::kCallbackStorage>;

/* Заявка на команду. Заповнюється призначеними ініціалізаторами на місці
   виклику, далі живе в черзі. Текст — без "\r\n": термінатор допише рушій,
   бо саме за цим текстом він потім упізнає луну. */
struct Command {
    StaticString<config::kMaxCommand> text{};
    StaticString<config::kMaxPrefix> expect{};

    /* Сирі байти, які підуть у дріт після запрошення '>'. Пам'ять належить
       тому, хто замовляв команду, і мусить жити до виклику done. */
    std::span<const std::byte> payload{};

    Millis timeout{1000};
    std::uint8_t retries{0};   // лише для таймаутів і тимчасових помилок
    bool wait_prompt{false};
    DoneCallback done{};

    std::uint8_t attempt{0};   // службове поле рушія
};

}  // namespace at
