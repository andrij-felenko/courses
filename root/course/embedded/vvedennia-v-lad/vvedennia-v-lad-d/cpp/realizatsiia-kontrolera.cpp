#include <string_view>
#include <string>
#include <array>
#include <span>
#include <variant>
#include <expected>
#include <cstdint>
#include <chrono>

namespace embedded::onboarding {

constexpr std::size_t MaxSsidLen = 32;
constexpr std::size_t MaxPassLen = 64;
constexpr std::size_t MaxEndpointLen = 128;
constexpr std::size_t ClaimTokenLen = 32;
constexpr std::size_t PopPinLen = 8;
constexpr auto ConfigTimeout = std::chrono::seconds(300);

enum class ErrorCode {
    InvalidState,
    AuthenticationFailed,
    NetworkTimeout,
    CloudRejected,
    StorageFault,
    MaxAttemptsExceeded
};

struct ProvisionPayload {
    std::string ssid;
    std::string passphrase;
    std::string cloud_endpoint;
    std::array<std::uint8_t, ClaimTokenLen> claim_token{};
    std::uint16_t cloud_port{8883};
};

/* Типізовані стани автомата */
struct StateFactoryReset {};
struct StateChannelListening {
    std::chrono::seconds elapsed{0};
    std::uint8_t failed_attempts{0};
};
struct StateAuthenticating {};
struct StateNetworkConnecting {
    ProvisionPayload config;
};
struct StateCloudEnrolling {
    ProvisionPayload config;
};
struct StateClaimedLocked {};

using OnboardState = std::variant<
    StateFactoryReset,
    StateChannelListening,
    StateAuthenticating,
    StateNetworkConnecting,
    StateCloudEnrolling,
    StateClaimedLocked
>;

/* Апаратний шар (концепт драйвера) */
class HardwareAdapter {
public:
    virtual ~HardwareAdapter() = default;
    virtual void start_advertising() = 0;
    virtual void stop_advertising() = 0;
    virtual bool connect_station(std::string_view ssid, std::string_view pass) = 0;
    virtual bool request_ldevid(std::string_view endpoint, std::uint16_t port,
                                std::span<const std::uint8_t, ClaimTokenLen> token) = 0;
    virtual bool save_ldevid() = 0;
};

class OnboardingController {
public:
    explicit OnboardingController(HardwareAdapter& hw, std::string_view factory_pin)
        : hw_(hw), factory_pin_(factory_pin), state_(StateFactoryReset{}) {}

    [[nodiscard]] std::expected<void, ErrorCode> start_listening() noexcept {
        if (std::holds_alternative<StateClaimedLocked>(state_)) {
            return std::unexpected(ErrorCode::InvalidState);
        }
        hw_.start_advertising();
        state_ = StateChannelListening{};
        return {};
    }

    [[nodiscard]] std::expected<void, ErrorCode> verify_pop(std::string_view pin) noexcept {
        auto* listening = std::get_if<StateChannelListening>(&state_);
        if (!listening) {
            return std::unexpected(ErrorCode::InvalidState);
        }

        if (listening->failed_attempts >= 3) {
            return std::unexpected(ErrorCode::MaxAttemptsExceeded);
        }

        if (pin == factory_pin_) {
            state_ = StateAuthenticating{};
            return {};
        }

        listening->failed_attempts++;
        return std::unexpected(ErrorCode::AuthenticationFailed);
    }

    [[nodiscard]] std::expected<void, ErrorCode> apply_configuration(ProvisionPayload payload) noexcept {
        if (!std::holds_alternative<StateAuthenticating>(state_)) {
            return std::unexpected(ErrorCode::InvalidState);
        }

        state_ = StateNetworkConnecting{payload};
        if (!hw_.connect_station(payload.ssid, payload.passphrase)) {
            state_ = StateChannelListening{};
            return std::unexpected(ErrorCode::NetworkTimeout);
        }

        state_ = StateCloudEnrolling{payload};
        if (!hw_.request_ldevid(payload.cloud_endpoint, payload.cloud_port, payload.claim_token)) {
            state_ = StateChannelListening{};
            return std::unexpected(ErrorCode::CloudRejected);
        }

        if (!hw_.save_ldevid()) {
            return std::unexpected(ErrorCode::StorageFault);
        }

        hw_.stop_advertising();
        state_ = StateClaimedLocked{};
        return {};
    }

    void on_timer_tick(std::chrono::seconds delta) noexcept {
        if (auto* listening = std::get_if<StateChannelListening>(&state_)) {
            listening->elapsed += delta;
            if (listening->elapsed >= ConfigTimeout) {
                hw_.stop_advertising();
                state_ = StateFactoryReset{};
            }
        }
    }

    [[nodiscard]] bool is_locked() const noexcept {
        return std::holds_alternative<StateClaimedLocked>(state_);
    }

private:
    HardwareAdapter& hw_;
    std::string factory_pin_;
    OnboardState state_;
};

} // namespace embedded::onboarding
