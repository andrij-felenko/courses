#pragma once

// Сесія offboard: сокет, телеметрія, команди й потік уставок в одному
// об'єкті з часом життя. Прибирання за собою — у деструкторі, тому гілок
// аварійного виходу тут немає взагалі.

#include <array>
#include <chrono>
#include <cstdint>
#include <expected>
#include <functional>
#include <optional>
#include <string>
#include <utility>

#include <netinet/in.h>
#include <sys/socket.h>

#include "setpoints.hpp"

namespace px4 {

using Clock = std::chrono::steady_clock;

/* Дескриптор під власником: у C ту саму роботу робили гілки goto out. */
class UniqueFd {
public:
    UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_{fd} {}

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_{std::exchange(other.fd_, -1)} {}
    UniqueFd& operator=(UniqueFd&& other) noexcept
    {
        if (this != &other) reset(std::exchange(other.fd_, -1));
        return *this;
    }

    ~UniqueFd() { reset(); }

    void reset(int fd = -1) noexcept;

    [[nodiscard]] int get() const noexcept { return fd_; }
    explicit operator bool() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

struct Telemetry {
    std::optional<Clock::time_point> heartbeat_at;
    std::uint8_t  base_mode{};
    std::uint32_t custom_mode{};
    std::uint8_t  system_status{};

    std::optional<sp::Vec3> position;   // LOCAL_POSITION_NED, м
    std::optional<sp::Vec3> velocity;   // м/с
    std::optional<float>    yaw;        // ATTITUDE, рад
    std::optional<std::uint16_t> estimator_flags;

    [[nodiscard]] bool armed() const noexcept
    {
        return (base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0;
    }
    [[nodiscard]] std::uint8_t main_mode() const noexcept
    {
        return static_cast<std::uint8_t>((custom_mode >> 16) & 0xFFu);
    }
    [[nodiscard]] bool offboard() const noexcept { return main_mode() == 6; }
    [[nodiscard]] bool alive(Clock::time_point now) const noexcept
    {
        return heartbeat_at && (now - *heartbeat_at) < std::chrono::milliseconds{1500};
    }
};

class OffboardSession {
public:
    /* Будівник уставки: аргумент — час від початку фази, секунди. */
    using Builder = std::function<std::expected<mavlink_message_t, sp::Error>(double)>;

    /* Помилки налаштування — винятки: далі однаково нічого робити.
       Відповіді автопілота — std::expected: це нормальний хід подій. */
    explicit OffboardSession(std::uint16_t local_port);
    ~OffboardSession();

    OffboardSession(const OffboardSession&) = delete;
    OffboardSession& operator=(const OffboardSession&) = delete;

    void wait_for_heartbeat(std::chrono::milliseconds timeout);

    [[nodiscard]] const Telemetry& telemetry() const noexcept { return tlm_; }
    [[nodiscard]] sp::Ids ids() const noexcept { return ids_; }

    std::expected<void, std::string> enable_offboard(const Builder& keepalive);
    std::expected<void, std::string> arm(bool on, const Builder& keepalive);
    std::expected<void, std::string> stream(std::chrono::milliseconds duration,
                                            const Builder& build,
                                            bool require_offboard = true);

private:
    void send(const mavlink_message_t& msg);
    void pump(std::chrono::milliseconds timeout);
    void handle(const mavlink_message_t& msg);
    void heartbeat_tick();
    void leave_offboard() noexcept;

    std::expected<std::uint8_t, std::string> send_command(std::uint16_t command,
                                                          std::array<float, 7> params,
                                                          std::uint8_t confirmation,
                                                          const Builder& keepalive,
                                                          std::chrono::milliseconds timeout);

    UniqueFd    fd_{};
    sockaddr_in peer_{};
    socklen_t   peer_len_{0};
    bool        peer_known_{false};

    sp::Ids   ids_{};
    Telemetry tlm_{};

    std::optional<std::pair<std::uint16_t, std::uint8_t>> ack_{};
    Clock::time_point last_heartbeat_sent_{};
    bool engaged_{false};   // ми справді ввели апарат в offboard
};

[[nodiscard]] std::string_view result_name(std::uint8_t result) noexcept;

}  // namespace px4
