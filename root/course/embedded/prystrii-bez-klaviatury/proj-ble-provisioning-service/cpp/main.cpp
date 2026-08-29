/*
 * Диспетчер GATT-сервісу провізіонування: звʼязує події BLE-стека
 * з криптографічною сесією, а результат Wi-Fi — зі сповіщеннями клієнту.
 */
#include <algorithm>
#include <array>
#include <cstdint>
#include <span>

#include "platform.hpp"
#include "reassembly.hpp"
#include "session.hpp"

namespace prov {
namespace {

[[maybe_unused]] constexpr std::uint16_t UuidService = 0xFF50;
constexpr std::uint16_t UuidSession = 0xFF51;
constexpr std::uint16_t UuidConfig = 0xFF52;

// Скільки тримати радіо після успіху, щоб сповіщення встигло вийти в ефір.
constexpr auto BleLinger = std::chrono::milliseconds{2000};

class ProvisioningService {
public:
    ProvisioningService() : session_{platform::pop_secret()} {}

    void start()
    {
        reassembler_.cancel();
        wipe_credentials(pending_);
        session_response_len_ = 0;
        mtu_ = AttMtuDefault;
        provisioned_ = false;
        platform::ble_advertise();
    }

    void on_connect()
    {
        mtu_ = AttMtuDefault;    // до узгодження живемо на базовому кадрі
        reassembler_.cancel();
    }

    std::uint16_t on_mtu_exchange(std::uint16_t client_mtu)
    {
        mtu_ = negotiate_mtu(client_mtu);
        return mtu_;             // стек відповість цим значенням клієнту
    }

    void on_write(std::uint16_t char_uuid, std::span<const std::uint8_t> data)
    {
        switch (char_uuid) {
        case UuidSession: handle_session_write(data); break;
        case UuidConfig:  handle_config_write(data);  break;
        default: break;          // чужий атрибут — не наша характеристика
        }
    }

    std::size_t on_read(std::uint16_t char_uuid, std::span<std::uint8_t> out)
    {
        if (char_uuid != UuidSession || session_response_len_ == 0) {
            return 0;
        }
        const std::size_t len = std::min(session_response_len_, out.size());
        std::copy_n(session_response_.begin(), len, out.begin());
        return len;              // довге читання клієнт добере за зміщенням
    }

    std::uint8_t on_prepare_write(std::uint16_t char_uuid, std::uint16_t offset,
                                  std::span<const std::uint8_t> value)
    {
        auto result = reassembler_.prepare(char_uuid, offset, value);
        return result ? 0x00 : static_cast<std::uint8_t>(result.error());
    }

    std::uint8_t on_execute_write(bool commit)
    {
        auto result = reassembler_.execute(commit);
        if (!result) {
            return static_cast<std::uint8_t>(result.error());
        }
        if (!result->value.empty()) {
            on_write(result->char_uuid, result->value);
        }
        reassembler_.cancel();   // зібране значення вже спожите
        return 0x00;
    }

    void on_wifi_event(platform::WifiEvent event, std::uint32_t ipv4)
    {
        using platform::WifiEvent;
        switch (event) {
        case WifiEvent::Connected:
            if (!platform::nvs_store_credentials(pending_.ssid, pending_.password)) {
                notify(Status::StorageFailure);
                break;
            }
            notify_success(ipv4);
            wipe_credentials(pending_);
            provisioned_ = true;
            platform::timer_once(BleLinger, &ProvisioningService::linger_expired);
            break;

        case WifiEvent::AuthFailed:
            // Сесію тримаємо відкритою: клієнт виправить пароль без нового пошуку.
            platform::wifi_stop();
            wipe_credentials(pending_);
            notify(Status::AuthenticationFailed);
            break;

        case WifiEvent::NoAccessPoint:
        case WifiEvent::Timeout:
            platform::wifi_stop();
            wipe_credentials(pending_);
            notify(Status::StationTimeout);
            break;
        }
    }

    void on_disconnect(std::uint8_t hci_reason)
    {
        (void)hci_reason;        // 0x08 — таймаут нагляду; для нас усі розриви однакові
        reassembler_.cancel();
        secure_wipe(session_response_);
        session_response_len_ = 0;
        wipe_credentials(pending_);
        session_.reset();
        mtu_ = AttMtuDefault;

        if (provisioned_) {
            platform::ble_shutdown();
        } else {
            platform::wifi_stop();   // незавершена перевірка пароля нікому не потрібна
            platform::ble_advertise();
        }
    }

    static ProvisioningService& instance()
    {
        static ProvisioningService service;
        return service;
    }

private:
    static void linger_expired()
    {
        auto& self = instance();
        self.session_.reset();
        self.reassembler_.cancel();
        platform::ble_shutdown();    // радіо вимкнене, RAM стека — застосунку
    }

    void handle_session_write(std::span<const std::uint8_t> data)
    {
        auto response = session_.handshake(data);
        if (!response) {
            secure_wipe(session_response_);
            session_response_len_ = 0;
            notify(response.error());
            return;
        }
        // За успіху клієнт забирає відповідь читанням prov-session.
        auto out = session_response_.begin();
        out = std::copy(response->device_public_key.begin(), response->device_public_key.end(), out);
        std::copy(response->salt.begin(), response->salt.end(), out);
        session_response_len_ = KeySize + SaltSize;
    }

    void handle_config_write(std::span<const std::uint8_t> data)
    {
        auto creds = session_.decrypt_config(data);
        if (!creds) {
            notify(creds.error());
            return;
        }
        // У NVS кладемо не зараз, а лише коли точка доступу справді пустила.
        pending_ = std::move(*creds);
        platform::wifi_connect(pending_.ssid, pending_.password);
    }

    // Сповіщення на prov-config: [статус 1] — влазить навіть у базові 20 байтів.
    void notify(Status status)
    {
        const std::array<std::uint8_t, 1> frame{static_cast<std::uint8_t>(status)};
        platform::ble_notify(UuidConfig, frame);
    }

    // [статус 1][IPv4 4] — сповіщення не фрагментується, тож мусить влазити
    // навіть у базовий кадр ATT.
    void notify_success(std::uint32_t ipv4)
    {
        constexpr std::size_t FrameLen = 1 + 4;
        static_assert(FrameLen <= mtu_payload(AttMtuDefault));

        const std::array<std::uint8_t, FrameLen> frame{
            static_cast<std::uint8_t>(Status::Success),
            static_cast<std::uint8_t>(ipv4 >> 24), static_cast<std::uint8_t>(ipv4 >> 16),
            static_cast<std::uint8_t>(ipv4 >> 8), static_cast<std::uint8_t>(ipv4)};
        platform::ble_notify(UuidConfig, frame);
    }

    ProvisioningSession session_;
    AttReassembler reassembler_;
    WifiCredentials pending_;
    std::array<std::uint8_t, KeySize + SaltSize> session_response_{};
    std::size_t session_response_len_{0};
    std::uint16_t mtu_{AttMtuDefault};
    bool provisioned_{false};
};

}  // namespace
}  // namespace prov

// Точки входу, які кличе BLE-стек. Сервіс 0xFF50 із характеристиками
// 0xFF51 (Write/Read) та 0xFF52 (Write/Notify) реєструє порт.
extern "C" {

void prov_service_start()
{
    prov::ProvisioningService::instance().start();
}

void prov_on_connect()
{
    prov::ProvisioningService::instance().on_connect();
}

void prov_on_disconnect(std::uint8_t hci_reason)
{
    prov::ProvisioningService::instance().on_disconnect(hci_reason);
}

std::uint16_t prov_on_mtu_exchange(std::uint16_t client_mtu)
{
    return prov::ProvisioningService::instance().on_mtu_exchange(client_mtu);
}

void prov_on_gatt_write(std::uint16_t char_uuid, const std::uint8_t* data, std::size_t len)
{
    prov::ProvisioningService::instance().on_write(char_uuid, {data, len});
}

std::size_t prov_on_gatt_read(std::uint16_t char_uuid, std::uint8_t* out, std::size_t max_len)
{
    return prov::ProvisioningService::instance().on_read(char_uuid, {out, max_len});
}

std::uint8_t prov_on_prepare_write(std::uint16_t char_uuid, std::uint16_t offset,
                                   const std::uint8_t* value, std::size_t len)
{
    return prov::ProvisioningService::instance().on_prepare_write(char_uuid, offset, {value, len});
}

std::uint8_t prov_on_execute_write(bool commit)
{
    return prov::ProvisioningService::instance().on_execute_write(commit);
}

void prov_on_wifi_event(prov::platform::WifiEvent event, std::uint32_t ipv4)
{
    prov::ProvisioningService::instance().on_wifi_event(event, ipv4);
}

}  // extern "C"
