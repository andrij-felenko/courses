// Кредитний обмін для шини без апаратних ліній керування.
//
// Ключ протоколу — КУМУЛЯТИВНЕ число звільнених слотів у кожному кадрі
// повернення. Втрачений GRANT тоді нічого не коштує: наступний кадр несе те
// саме абсолютне число, і баланс сходиться сам. Проти повної тиші є таймер
// неактивності й запит стану POLL.
#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string_view>

namespace credit {

using Millis = std::chrono::milliseconds;

inline constexpr std::size_t kMaxPayload = 64;
inline constexpr std::uint16_t kWindow = 4;      // скільки кадрів приймач тримає одночасно
inline constexpr std::uint16_t kGrantBatch = 2;  // стільки звільнень копимо перед GRANT
inline constexpr Millis kPollTimeout{250};
inline constexpr std::uint8_t kMaxPolls = 5;

enum class FrameKind : std::uint8_t { Data = 1, Grant = 2, Poll = 3 };

// Кадр збирається лише іменованими фабриками: зібрати DATA без корисних даних
// або GRANT із номером послідовності тут неможливо за побудовою.
class Frame {
public:
    Frame() = default;

    [[nodiscard]] static Frame make_data(std::uint8_t seq,
                                         std::span<const std::uint8_t> payload) noexcept;
    [[nodiscard]] static Frame make_grant(std::uint16_t cumulative) noexcept;
    [[nodiscard]] static Frame make_poll(std::uint16_t cumulative) noexcept;

    [[nodiscard]] FrameKind kind() const noexcept { return kind_; }
    [[nodiscard]] std::uint8_t seq() const noexcept { return seq_; }
    [[nodiscard]] std::uint16_t cumulative_release() const noexcept { return cumulative_; }
    [[nodiscard]] std::span<const std::uint8_t> payload() const noexcept
    {
        return std::span{payload_}.first(length_);
    }

private:
    FrameKind kind_{FrameKind::Data};
    std::uint8_t seq_{0};
    std::uint16_t cumulative_{0};
    std::uint8_t length_{0};
    std::array<std::uint8_t, kMaxPayload> payload_{};
};

enum class LinkState : std::uint8_t {
    Ready,   // кредити є
    Blocked, // баланс нульовий, чекаємо повернення
    Polling, // мовчання затяглося, шлемо запити стану
    Dead     // відповіді немає й після kMaxPolls
};

[[nodiscard]] std::string_view to_string(LinkState state) noexcept;

enum class SendError : std::uint8_t { NoCredit, PayloadTooLong, LinkDown };
enum class RxError : std::uint8_t { OverQuota, MalformedFrame };

class Sender {
public:
    struct Stats {
        std::uint32_t frames_sent{0};
        std::uint32_t credits_granted{0};
        std::uint32_t stale_grants{0};   // кадр не приніс нічого нового
        std::uint32_t suspect_grants{0}; // приріст більший за вікно — кадр побито
    };

    explicit Sender(Millis now, std::uint16_t window = kWindow) noexcept;

    [[nodiscard]] bool can_send() const noexcept;
    [[nodiscard]] std::expected<Frame, SendError> encode(std::span<const std::uint8_t> payload,
                                                         Millis now) noexcept;
    // Будь-який кадр із того боку несе кумулятивне число — це і є піггібекінг.
    void on_frame(const Frame& frame, Millis now) noexcept;
    // Таймер неактивності: кадр запиту стану, коли лінк застряг.
    [[nodiscard]] std::optional<Frame> tick(Millis now) noexcept;

    [[nodiscard]] LinkState state() const noexcept { return state_; }
    [[nodiscard]] std::int32_t credits() const noexcept { return credits_; }
    [[nodiscard]] std::uint8_t polls_sent() const noexcept { return polls_sent_; }
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

private:
    std::int32_t window_;
    std::int32_t credits_;
    std::uint16_t last_cumulative_{0};
    std::uint8_t next_seq_{0};
    std::uint8_t polls_sent_{0};
    LinkState state_{LinkState::Ready};
    Millis last_event_{0};
    Stats stats_{};
};

class Receiver {
public:
    enum class Disposition : std::uint8_t { Stored, PollPending };

    struct Stats {
        std::uint32_t over_quota{0};
        std::uint32_t malformed{0};
        std::uint32_t seq_gaps{0}; // кадр даних загубився на шині
    };

    [[nodiscard]] std::expected<Disposition, RxError> accept(const Frame& frame) noexcept;
    // Завдання забирає найстаріший пакет; слот звільняється саме тут.
    [[nodiscard]] std::optional<Frame> take() noexcept;
    // Пачка назбиралася або прийшов POLL — формуємо кадр повернення.
    [[nodiscard]] std::optional<Frame> build_grant() noexcept;

    [[nodiscard]] std::size_t occupied() const noexcept { return occupied_; }
    [[nodiscard]] std::uint16_t cumulative_release() const noexcept { return cumulative_; }
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

private:
    std::array<Frame, kWindow> slots_{};
    std::size_t write_idx_{0};
    std::size_t read_idx_{0};
    std::size_t occupied_{0};
    std::uint16_t cumulative_{0};    // скільки слотів звільнено за весь час
    std::uint16_t last_reported_{0}; // яке число вже пішло в ефір
    std::uint8_t expected_seq_{0};
    bool seq_seen_{false};
    bool poll_pending_{false};
    Stats stats_{};
};

} // namespace credit
