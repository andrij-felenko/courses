#pragma once

#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

#include "firmware_descriptor.hpp"

namespace board {

/* Геометрія Flash конкретного виробу. Ці числа — не «налаштування»: вони
   зашиті в лінкерний скрипт застосунку, і дескриптор мусить із ними
   збігатися, інакше образ зібрано під іншу карту пам'яті. */
inline constexpr std::uint32_t flash_base   = 0x08000000u;
inline constexpr std::uint32_t flash_size   = 2048u * 1024u;

inline constexpr std::uint32_t app_header_address  = 0x08020000u;                 // 128 КБ під завантажувач
inline constexpr std::uint32_t app_payload_address = app_header_address + fw::descriptor_size;
inline constexpr std::uint32_t app_max_payload     = 896u * 1024u;

inline constexpr std::uint32_t ram_base = 0x20000000u;
inline constexpr std::uint32_t ram_size = 128u * 1024u;

/* Ідентифікатор виробу зашивається на збірці завантажувача: одна плата —
   один код. Зміна коду означає новий виріб, а не нову опцію. */
inline constexpr std::uint32_t hw_platform_id = 0x0000A110u;   // датчик тиску

void early_init() noexcept;

/* Ревізія плати, зчитана зі strapping-виводів. */
[[nodiscard]] std::uint8_t pcb_revision() noexcept;

/* Монотонний лічильник безпеки в OTP: скільки рівнів уже пропалено. */
[[nodiscard]] std::uint32_t security_counter() noexcept;

/* Пропалює OTP до рівня level. Операція незворотна; false — відмова Flash
   або спроба вийти за межі блока. */
[[nodiscard]] bool burn_security_counter(std::uint32_t level) noexcept;

/* Кореневий відкритий ключ з OTP. Порожньо — пристрій не пройшов
   заводської персоналізації, перевіряти підпис нема чим. */
[[nodiscard]] std::optional<fw::PublicKey> root_public_key() noexcept;

/* Вікно у відображену в адресний простір Flash. Порожній span означає, що
   діапазон виходить за межі кристала. */
[[nodiscard]] std::span<const std::byte> flash_window(std::uint32_t address,
                                                      std::size_t size) noexcept;

void led(bool on) noexcept;
void delay_ms(std::uint32_t ms) noexcept;

}  // namespace board
