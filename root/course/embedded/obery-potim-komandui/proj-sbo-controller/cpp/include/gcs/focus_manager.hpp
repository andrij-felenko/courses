// focus_manager.hpp — замок цілі на пульті: що обрано, чи підтверджено, чи можна тиснути.
#pragma once

#include "sbo/protocol.hpp"

#include <array>
#include <chrono>
#include <string_view>

namespace gcs {

// Скільки чекаємо квитанції по радіо, перш ніж визнати звʼязок утраченим.
inline constexpr std::chrono::milliseconds kAckTimeout{400};
// Запас, на який пульт закриває вікно раніше за борт: кадр іще має долетіти.
inline constexpr std::chrono::milliseconds kGuard{150};
inline constexpr std::size_t kNameLen = 16;

enum class Status : std::uint8_t {
    None = 0,   // апарат не обрано
    WaitAck,    // SELECT_REQ надіслано, чекаємо квитанції
    Armed,      // борт підтвердив: кнопка дії активна
    WaitOp,     // OPERATE_REQ надіслано, чекаємо квитанції
    Done,       // борт відзвітував про виконання
    LinkLost,   // квитанція не надійшла за kAckTimeout
    Rejected,   // борт відмовив
    Expired     // вікно селекції спливло без дії
};

class FocusManager {
public:
    using Clock     = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    explicit FocusManager(sbo::NodeId self = sbo::NodeId{sbo::kGcsDefaultId}) noexcept;

    // Клік по картці апарата: кадр SELECT_REQ і запуск відліку квитанції.
    [[nodiscard]] std::expected<sbo::Frame, sbo::Error>
    select(sbo::NodeId target, std::uint8_t component, std::string_view name,
           sbo::CommandCode cmd, std::chrono::milliseconds window, TimePoint now) noexcept;

    void tick(TimePoint now) noexcept;                       // з циклу перемальовування
    void on_response(const sbo::Frame& rx, TimePoint now) noexcept;

    // Кнопка дії: віддає кадр лише зі зведеним замком і лише один раз.
    [[nodiscard]] std::expected<sbo::Frame, sbo::Error>
    build_operate(std::span<const std::uint8_t> payload, TimePoint now) noexcept;

    [[nodiscard]] std::expected<sbo::Frame, sbo::Error> build_cancel(TimePoint now) noexcept;

    [[nodiscard]] bool             button_enabled(TimePoint now) const noexcept;
    [[nodiscard]] Status           status() const noexcept { return status_; }
    [[nodiscard]] sbo::NodeId      target_id() const noexcept { return target_; }
    [[nodiscard]] std::string_view target_name() const noexcept;
    [[nodiscard]] std::string_view badge() const noexcept;    // підпис на картці
    [[nodiscard]] std::uint32_t    frame_color() const noexcept;  // 0xRRGGBB рамки

private:
    [[nodiscard]] sbo::Frame request(sbo::MessageType type) noexcept;

    sbo::NodeId      self_;
    sbo::NodeId      target_{};
    std::uint8_t     component_{0};
    std::array<char, kNameLen> name_{};
    sbo::CommandCode pending_cmd_{};
    sbo::Token       token_{};
    std::chrono::milliseconds window_{sbo::kDefaultWindow};
    TimePoint        sent_at_{};
    TimePoint        ack_deadline_{};
    TimePoint        select_deadline_{};
    std::uint8_t     seq_{0};
    Status           status_{Status::None};
    sbo::Error       last_error_{sbo::Error::InternalFault};
};

}  // namespace gcs
