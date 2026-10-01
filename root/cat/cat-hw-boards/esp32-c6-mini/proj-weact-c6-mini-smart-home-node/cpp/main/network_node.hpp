#pragma once

#include <cstdint>
#include <span>
#include <array>
#include "esp_err.h"
#include "esp_ieee802154.h"

namespace iot {

/// Конфігураційні параметри бездротового стеку IEEE 802.15.4
struct NetworkConfig {
    uint8_t channel{15};                // Радіоканал (11-26)
    uint16_t pan_id{0x1234};            // Ідентифікатор мережі PAN ID
    uint16_t short_addr{0x0002};        // Коротка мережева адреса пристрою
    uint16_t dest_addr{0x0001};         // Адреса приймача (шлюзу)
    int8_t tx_power_dbm{20};            // Потужність передачі в dBm
};

/// Клас керування радіомодулем 802.15.4 для мереж Thread та Zigbee
class NetworkNode {
public:
    explicit NetworkNode(NetworkConfig config = {}) noexcept;
    ~NetworkNode();

    NetworkNode(const NetworkNode&) = delete;
    NetworkNode& operator=(const NetworkNode&) = delete;

    NetworkNode(NetworkNode&&) noexcept;
    NetworkNode& operator=(NetworkNode&&) noexcept;

    /// Ініціалізація радіостеку 802.15.4
    [[nodiscard]] esp_err_t initialize() noexcept;

    /// Передача телеметричного пакета в радіоефір
    [[nodiscard]] esp_err_t transmit_data(std::span<const uint8_t> payload) noexcept;

    /// Деактивація радіомодуля перед переходом у Deep Sleep
    esp_err_t disable_radio() noexcept;

private:
    NetworkConfig config_;
    bool is_initialized_{false};
    uint8_t mac_seq_num_{0};

    [[nodiscard]] std::array<uint8_t, 127> build_ieee802154_frame(std::span<const uint8_t> payload, uint8_t& out_frame_len) noexcept;
};

} // namespace iot
