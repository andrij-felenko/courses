#pragma once

#include <cstdint>
#include <expected>
#include <functional>
#include <optional>
#include <random>
#include <span>
#include <unordered_map>

#include "frame.hpp"
#include "protocol.hpp"

namespace auth {

// Бортовий арбітр повноважень: єдине місце, де вирішується, чиї кадри
// доходять до контурів керування.
class Arbiter {
public:
    // Куди борт віддає власні кадри (радіомодем, UART, сокет).
    using Emit = std::function<void(std::span<const std::byte>)>;

    Arbiter(std::uint8_t self_id, std::uint32_t commander_key, Emit emit);

    // Обробка одного вхідного кадру з мережі.
    std::expected<void, StatusCode> handle(std::span<const std::byte> raw, Ms now);

    // Періодичний хід годинника: тайм-аути оренди та передачі зміни.
    [[nodiscard]] Failsafe tick(Ms now);

    // Фільтр керівних пакетів на 50 Гц.
    [[nodiscard]] bool accept_control(std::uint8_t source_id, std::uint32_t nonce,
                                      Role plane, Ms now) const noexcept;

    // Поточне положення газу борту — під нього вирівнюється змінний пілот.
    void set_vehicle_throttle(std::int16_t throttle) noexcept { vehicle_throttle_ = throttle; }

    [[nodiscard]] ArbitrationStatus status(Ms now) const noexcept;

private:
    struct Token {
        std::uint8_t  gcs{0};
        std::uint32_t nonce{0};
        Ms            lease_deadline{0};

        [[nodiscard]] bool active(Ms now) const noexcept {
            return gcs != 0 && nonce != 0 && now < lease_deadline;
        }
        void clear() noexcept { *this = Token{}; }
    };

    struct Handover {
        std::uint8_t from{0};
        std::uint8_t to{0};
        Ms           deadline{0};
    };

    std::expected<void, StatusCode> on_heartbeat(const Frame& f, Ms now);
    std::expected<void, StatusCode> on_token_request(const Frame& f, Ms now);
    std::expected<void, StatusCode> on_stick_check(const Frame& f, Ms now);
    std::expected<void, StatusCode> on_override(const Frame& f, Ms now);

    std::expected<void, StatusCode> grant_exclusive(Token& token, Role role,
                                                    const Frame& f, Ms now);
    std::expected<void, StatusCode> start_handover(const Frame& f, std::uint8_t target, Ms now);

    template <class T>
    void send(std::uint8_t target, const T& body, Ms now, std::uint32_t nonce = 0);

    void reply_grant(std::uint8_t target, Role role, StatusCode status,
                     std::uint32_t nonce, Ms now);
    void send_revoke(std::uint8_t target, Role role, RevokeReason reason, Ms now);
    void broadcast_status(Ms now);

    [[nodiscard]] std::uint32_t next_nonce();
    [[nodiscard]] bool seq_ok(std::uint8_t gcs, std::uint16_t seq);

    std::uint8_t  self_id_;
    std::uint32_t commander_key_;
    Emit          emit_;

    std::mt19937  rng_{0xA5A50F0F};
    std::uint16_t tx_seq_{0};

    Token pilot_{};
    Token payload_{};
    Token commander_{};

    ArbitrationState        state_{ArbitrationState::Idle};
    std::optional<Handover> handover_{};
    std::int16_t            vehicle_throttle_{0};
    Failsafe                pending_failsafe_{Failsafe::None};

    std::unordered_map<std::uint8_t, std::uint16_t> last_seq_{};
};

}  // namespace auth
