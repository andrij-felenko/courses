// FlightRecorderCore.cpp — розміщення тому в незанулюваній пам'яті.
#include "FlightRecorderCore.hpp"

namespace embedded::diagnostics {
namespace {

// Секція .noinit виключена зі списку тих, що їх занулює стартовий код, тому
// вміст переживає і скидання ядра, і спрацювання сторожового таймера.
// Ініціалізатори класу — суцільно constexpr, тож жоден конструктор не
// виконується під час запуску й не затирає накопичену хронологію.
[[gnu::section(".noinit")]] Recorder g_flight_recorder;

static_assert(std::is_trivially_destructible_v<Recorder>,
              "том у .noinit не має права на деструктор під час завершення програми");

} // namespace

Recorder& recorder() noexcept { return g_flight_recorder; }

} // namespace embedded::diagnostics

// Тонкі перехідники для коду на C — драйверів і обробників переривань,
// які не збираються компілятором C++.
extern "C" {

std::uint8_t blackbox_init_cpp(void) {
    return static_cast<std::uint8_t>(embedded::diagnostics::recorder().init());
}

void blackbox_release_cpp(void) {
    embedded::diagnostics::recorder().release();
}

void blackbox_log_cpp(std::uint8_t subsystem, std::uint8_t code, std::uint16_t fsm,
                      const void* data, std::uint8_t len) {
    const auto* bytes = static_cast<const std::byte*>(data);
    embedded::diagnostics::recorder().log(
        static_cast<embedded::diagnostics::Subsystem>(subsystem),
        static_cast<embedded::diagnostics::EventCode>(code), fsm,
        bytes != nullptr ? std::span<const std::byte>{bytes, len} : std::span<const std::byte>{});
}

} // extern "C"
