#pragma once

#include <algorithm>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <span>

#include "mcu/startup.hpp"

/* Символи лінкера зручно оголошувати масивами невідомого розміру: ім'я
   саме розпадається на покажчик, і не треба писати & перед кожним. */
extern "C" {
extern std::uint32_t _sidata[]; /* образ .data у Flash (LMA) */
extern std::uint32_t _sdata[];  /* .data у RAM (VMA) */
extern std::uint32_t _edata[];
extern std::uint32_t _sbss[];
extern std::uint32_t _ebss[];
}

namespace mcu {

[[nodiscard]] inline std::span<std::uint32_t> data_section() noexcept
{
    return {_sdata, static_cast<std::size_t>(_edata - _sdata)};
}

[[nodiscard]] inline std::span<std::uint32_t> bss_section() noexcept
{
    return {_sbss, static_cast<std::size_t>(_ebss - _sbss)};
}

/* Розгортання робочого простору змінних. Викликається до першого
   звертання до глобальних даних, тож сама функція їх не торкається:
   усе, чим вона користується, лежить на стеку або в регістрах. */
inline void init_memory() noexcept
{
    /* Робота 32-бітними словами правильна лише за вирівняними межами
       секцій — їх дає `. = ALIGN(4);` у скрипті лінкера. Незарівняний
       кінець .data мовчки затер би перший байт сусідньої .bss. */
    const auto bounds = std::bit_cast<std::uintptr_t>(_sidata)
                      | std::bit_cast<std::uintptr_t>(_sdata)
                      | std::bit_cast<std::uintptr_t>(_edata)
                      | std::bit_cast<std::uintptr_t>(_sbss)
                      | std::bit_cast<std::uintptr_t>(_ebss);
    if ((bounds % sizeof(std::uint32_t)) != 0U) {
        trap();
    }

    const auto data = data_section();

    /* Прошивка, зібрана на виконання просто з Flash, має LMA == VMA:
       джерело й ціль — та сама пам'ять, копіювати нема чого. */
    if (_sidata != _sdata) {
        const std::span<const std::uint32_t> image{_sidata, data.size()};
        std::ranges::copy(image, data.begin());
    }

    /* .bss у прошивці не займає жодного байта — нулі створюємо тут */
    std::ranges::fill(bss_section(), 0U);
}

} // namespace mcu
