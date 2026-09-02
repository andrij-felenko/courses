#include <array>
#include <cstdint>
#include <format>
#include <print>
#include <string>
#include <string_view>

#include "fixed.hpp"
#include "iir.hpp"
#include "raw_frame.hpp"
#include "sensor_si.hpp"

namespace {

// Кадр із вступу: шість байтів одного пакетного читання по SPI.
constexpr std::array<std::uint8_t, 6> kFrame{0xF0, 0x0F, 0x00, 0x08, 0x40, 0x01};

template <class Q>
[[nodiscard]] std::string milli(Q q) {
    const std::int32_t v = q.count();
    const std::int32_t a = v < 0 ? -v : v;
    return std::format("{}{}.{:03} {}", v < 0 ? "-" : "", a / 1000, a % 1000, Q::unit);
}

void show_axes(std::string_view title, raw::Vec3Raw f) {
    const auto v = si::accel_from_frame(f);
    std::println("  {}", title);
    std::println("    сирі відліки   X={} Y={} Z={}", f.x, f.y, f.z);
    std::println("    X={}  Y={}  Z={}", milli(v.x), milli(v.y), milli(v.z));
    std::println("    модуль {}", milli(v.magnitude()));
}

void demo_frame() {
    std::println("Розбір кадру 0xF0 0x0F 0x00 0x08 0x40 0x01:");

    // Хиба перша: порядок байтів переплутано.
    show_axes("порядок байтів переплутано", raw::parse_be16(std::span{kFrame}));

    // Хиба друга: порядок правильний, знакового розширення 12 бітів немає.
    const raw::Vec3Raw no_sign{
        static_cast<std::int16_t>(raw::assemble_le(kFrame[0], kFrame[1])),
        static_cast<std::int16_t>(raw::assemble_le(kFrame[2], kFrame[3])),
        static_cast<std::int16_t>(raw::assemble_le(kFrame[4], kFrame[5]))};
    show_axes("без знакового розширення", no_sign);

    // Як треба — і довжину буфера перевіряє тип результату.
    const auto parsed = raw::parse<12>(std::span<const std::uint8_t>{kFrame},
                                       raw::Layout::right_aligned_le);
    if (!parsed) {
        std::println("  кадр коротший за шість байтів — читання відкинуто");
        return;
    }
    show_axes("правильний розбір", *parsed);

    // Коротка відповідь шини не мовчить і не дає сміття.
    const auto truncated = raw::parse<12>(std::span<const std::uint8_t>{kFrame}.first(3),
                                          raw::Layout::right_aligned_le);
    std::println("  обірваний кадр: {}", truncated.has_value() ? "прийнято" : "відкинуто");
}

void demo_filter() {
    dsp::ExpFilter<si::Acceleration, 3> filter;
    std::int16_t naive_state = 0;

    (void)filter.update(si::Acceleration{0});
    for (int n = 0; n < 64; ++n) {
        (void)dsp::naive_update<3>(naive_state, 1000);
        (void)filter.update(si::Acceleration{1000});
    }

    std::println("Мертва зона зсуву проти накопичувача Q16.16 (ціль 1000):");
    std::println("  наївний (стан у цілих): {} — застряг", naive_state);
    std::println("  накопичувач Q16.16:     {}", filter.value()->count());
}

void demo_units() {
    std::println("Масштабні коефіцієнти:");
    std::println("  TMP117      {}", milli(si::tmp117(3200)));
    std::println("  MCP9808     {}", milli(si::mcp9808(400)));
    std::println("  гіроскоп    {}", milli(si::gyro_from_lsb(28571)));
    std::println("  магнітометр {}", milli(si::mag_from_lsb(6842)));

    // Свідома демонстрація переповнення: добуток обрізається по 2^16.
    const auto broken = static_cast<std::uint16_t>(4095u * 3300u) / 4095u;
    std::println("АЦП 12 біт при опорних 3300 мВ:");
    std::println("  у 16 бітах  {} мВ", broken);
    std::println("  у 32 бітах  {}", milli(si::adc12_to_voltage(4095, 3300)));

    // Ділення, яке не має відповіді, повертає помилку типом.
    const auto bad = fx::Q16::from_int(1).divide(fx::Q16{});
    std::println("  ділення на нуль: {}", bad.has_value() ? "тихо пройшло" : "спіймано типом");
}

} // namespace

int main() {
    demo_frame();
    demo_filter();
    demo_units();
    return 0;
}
