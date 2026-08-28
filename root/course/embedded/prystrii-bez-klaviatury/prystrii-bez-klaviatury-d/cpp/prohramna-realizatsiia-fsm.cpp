#include <string>
#include <string_view>
#include <optional>
#include <variant>
#include <cstdint>

namespace fsm {

enum class State {
    Init,
    ConnectSaved,
    ProvisioningActive,
    Validating,
    Operational,
    ProvisioningFailed
};

struct Credentials {
    std::string ssid;
    std::string password;
};

// Події автомата
struct EvtStart {};
struct EvtCredentialsReceived { Credentials creds; };
struct EvtStationConnected {};
struct EvtStationAuthFail {};
struct EvtStationNotFound {};
struct EvtRetryTimeout {};
struct EvtFactoryReset {};

using Event = std::variant<
    EvtStart,
    EvtCredentialsReceived,
    EvtStationConnected,
    EvtStationAuthFail,
    EvtStationNotFound,
    EvtRetryTimeout,
    EvtFactoryReset
>;

// Абстрактний інтерфейс драйвера платформи
class IPlatformDriver {
public:
    virtual ~IPlatformDriver() = default;
    virtual std::optional<Credentials> read_nvs() = 0;
    virtual bool write_nvs(const Credentials& creds) = 0;
    virtual void erase_nvs() = 0;
    virtual void start_station(std::string_view ssid, std::string_view password) = 0;
    virtual void start_ble_provisioning() = 0;
    virtual void stop_ble_provisioning() = 0;
    virtual void notify_provisioning_status(int status_code) = 0;
};

class ProvisioningStateMachine {
public:
    explicit ProvisioningStateMachine(IPlatformDriver& driver)
        : driver_(driver), state_(State::Init) {}

    void dispatch(const Event& event) {
        if (std::holds_alternative<EvtFactoryReset>(event)) {
            driver_.erase_nvs();
            driver_.start_ble_provisioning();
            state_ = State::ProvisioningActive;
            return;
        }

        switch (state_) {
        case State::Init:
            handle_init(event);
            break;
        case State::ConnectSaved:
            handle_connect_saved(event);
            break;
        case State::ProvisioningActive:
            handle_prov_active(event);
            break;
        case State::Validating:
            handle_validating(event);
            break;
        case State::ProvisioningFailed:
            handle_prov_failed(event);
            break;
        case State::Operational:
            break;
        }
    }

    [[nodiscard]] State current_state() const noexcept { return state_; }

private:
    void handle_init(const Event& event) {
        if (std::holds_alternative<EvtStart>(event)) {
            auto saved = driver_.read_nvs();
            if (saved.has_value()) {
                current_creds_ = std::move(*saved);
                driver_.start_station(current_creds_.ssid, current_creds_.password);
                retry_count_ = 0;
                state_ = State::ConnectSaved;
            } else {
                driver_.start_ble_provisioning();
                state_ = State::ProvisioningActive;
            }
        }
    }

    void handle_connect_saved(const Event& event) {
        if (std::holds_alternative<EvtStationConnected>(event)) {
            state_ = State::Operational;
        } else if (std::holds_alternative<EvtStationAuthFail>(event) ||
                   std::holds_alternative<EvtStationNotFound>(event)) {
            if (++retry_count_ >= 3) {
                driver_.start_ble_provisioning();
                state_ = State::ProvisioningActive;
            } else {
                driver_.start_station(current_creds_.ssid, current_creds_.password);
            }
        }
    }

    void handle_prov_active(const Event& event) {
        if (const auto* rx = std::get_if<EvtCredentialsReceived>(&event)) {
            pending_creds_ = rx->creds;
            driver_.start_station(pending_creds_.ssid, pending_creds_.password);
            state_ = State::Validating;
        }
    }

    void handle_validating(const Event& event) {
        if (std::holds_alternative<EvtStationConnected>(event)) {
            current_creds_ = pending_creds_;
            driver_.write_nvs(current_creds_);
            driver_.notify_provisioning_status(0); // 0 = OK
            driver_.stop_ble_provisioning();
            state_ = State::Operational;
        } else if (std::holds_alternative<EvtStationAuthFail>(event)) {
            driver_.notify_provisioning_status(1); // 1 = Auth error
            state_ = State::ProvisioningFailed;
        } else if (std::holds_alternative<EvtStationNotFound>(event)) {
            driver_.notify_provisioning_status(2); // 2 = AP not found
            state_ = State::ProvisioningFailed;
        }
    }

    void handle_prov_failed(const Event& event) {
        if (const auto* rx = std::get_if<EvtCredentialsReceived>(&event)) {
            pending_creds_ = rx->creds;
            driver_.start_station(pending_creds_.ssid, pending_creds_.password);
            state_ = State::Validating;
        } else if (std::holds_alternative<EvtRetryTimeout>(event)) {
            state_ = State::ProvisioningActive;
        }
    }

    IPlatformDriver& driver_;
    State state_;
    uint8_t retry_count_{0};
    Credentials current_creds_{};
    Credentials pending_creds_{};
};

} // namespace fsm
