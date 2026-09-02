// Точки входу демонстрацій. Бібліотечна частина (політики, вартовий,
// лічильники) живе в include/mcu; тут — лише те, що показує стаття.
#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace demo {

// race_demo.cpp — незахищений спільний стан
void process_data() noexcept;
[[nodiscard]] std::uint32_t packet_counter() noexcept;

// naive_flags.cpp — наївна секція без збереження маски
void update_system_state(std::uint32_t flags) noexcept;
[[nodiscard]] std::uint32_t system_flags() noexcept;

// naive_uart_trap.cpp — зламана вкладеність у драйвері
[[nodiscard]] bool telemetry_send_packet(std::span<const std::byte> payload) noexcept;

// sensor_frame.cpp — витік маски й той самий код на вартовому
enum class FrameError : std::uint8_t { BadArgument, BadMark, BadChecksum };

[[nodiscard]] std::expected<void, FrameError>
handle_frame_manual(std::span<const std::byte> frame) noexcept;
[[nodiscard]] std::expected<void, FrameError>
handle_frame(std::span<const std::byte> frame) noexcept;
[[nodiscard]] std::uint16_t last_sample() noexcept;

// dual_core.cpp — друге ядро й апаратний спінлок
enum class MailboxError : std::uint8_t { LockTimeout };

[[nodiscard]] std::expected<void, MailboxError> mailbox_publish(std::int32_t setpoint_ma,
                                                                std::int32_t measured_ma) noexcept;
[[nodiscard]] std::expected<std::int32_t, MailboxError> mailbox_read_setpoint() noexcept;

} // namespace demo
