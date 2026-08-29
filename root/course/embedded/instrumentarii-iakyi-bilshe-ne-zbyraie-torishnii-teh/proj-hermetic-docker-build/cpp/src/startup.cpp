// Старт прошивки: перенесення .data, обнулення .bss і самоперевірка образу
// за метаданими збірки. Вирок лишається в скриньці .noinit, яку читає
// бутлоадер або зневаджувач.

#include "fw/build_meta.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

extern "C" {
// Символи розкладки з c/linker.ld — той самий скрипт компонувальника
extern std::byte __data_load[];
extern std::byte __data_start[];
extern std::byte __data_end[];
extern std::byte __bss_start[];
extern std::byte __bss_end[];
extern std::byte __image_start[];
extern std::byte __image_end[];
extern std::uint32_t _estack;

void Reset_Handler();
void Default_Handler();
}

namespace {

struct DiagBlock {
    std::uint32_t status;
    std::array<char, 160> text;
};

// .noinit стартовий код не чистить: вирок переживає теплий перезапуск
[[gnu::section(".noinit"), gnu::used]] DiagBlock g_diag;

std::span<const std::byte> imageSpan() noexcept
{
    return {__image_start, static_cast<std::size_t>(__image_end - __image_start)};
}

void run() noexcept
{
    const fw::Meta& meta = fw::currentMeta();
    const auto result = fw::verify(meta, imageSpan());

    // Звіт складаємо завжди: навіть при поганому CRC корисно бачити,
    // який коміт і який тулчейн дали цей образ.
    std::span<char> line{g_diag.text};
    const auto written = fw::report(line, meta);
    std::span<char> tail = line.subspan(written.size());

    const std::string_view verdict = result ? std::string_view{"ok"} : fw::describe(result.error());
    for (const std::string_view part : {std::string_view{" status="}, verdict}) {
        const auto n = std::min(tail.size(), part.size());
        std::ranges::copy_n(part.begin(), static_cast<std::ptrdiff_t>(n), tail.begin());
        tail = tail.subspan(n);
    }
    std::ranges::fill(tail, '\0');

    g_diag.status = result ? 0U : static_cast<std::uint32_t>(result.error()) + 1U;

    if (!result) {
        // Керування далі не віддаємо: образ не той, за який себе видає.
        while (true) {
        }
    }

    while (true) {
        __asm__ volatile("wfi");
    }
}

}  // namespace

extern "C" void Reset_Handler()
{
    const std::span<std::byte> data{__data_start,
                                    static_cast<std::size_t>(__data_end - __data_start)};
    std::ranges::copy_n(__data_load, static_cast<std::ptrdiff_t>(data.size()), data.begin());

    const std::span<std::byte> bss{__bss_start,
                                   static_cast<std::size_t>(__bss_end - __bss_start)};
    std::ranges::fill(bss, std::byte{0});

    run();
}

extern "C" void Default_Handler()
{
    // Рятувати нічого: зупиняємось, лишаючи стан зневаджувачу
    while (true) {
    }
}

extern "C" {
using Handler = void (*)();

[[gnu::section(".vectors"), gnu::used]]
constinit const std::array<Handler, 4> g_vectors{
    reinterpret_cast<Handler>(&_estack),  // початкове значення SP
    &Reset_Handler,
    &Default_Handler,  // NMI
    &Default_Handler   // HardFault
};
}
