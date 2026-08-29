// telemetry.hpp — вивід стенда через USART0, 115200 8N1.
//
// Рядок телеметрії — 30…40 символів. Віддати його блокуючим циклом означає
// з'їсти ~3 мс із такту в 5 мс: контур почав би спізнюватися саме тоді, коли
// ми його вимірюємо. У такті ми лише кладемо байти в кільце, а вивозить їх
// переривання спорожнілого регістра передавача.

#pragma once

#include <cstdint>
#include <string_view>

namespace gimbal::telemetry {

void begin(std::uint32_t baud) noexcept;

// Якщо в кільці немає місця — ТИХО відкидає. Телеметрія ніколи не має
// права затримати контур керування.
void write(std::string_view text) noexcept;
void write(std::int32_t value) noexcept;

// Скільки байтів загублено через переповнення. Росте — знижуй частоту
// виводу, інакше графік бреше.
[[nodiscard]] std::uint16_t dropped() noexcept;

}  // namespace gimbal::telemetry
