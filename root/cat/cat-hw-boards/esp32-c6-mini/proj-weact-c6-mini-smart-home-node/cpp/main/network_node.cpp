#include "network_node.hpp"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <cstring>
#include <algorithm>

namespace iot {

static const char* TAG = "NetworkNode";

NetworkNode::NetworkNode(NetworkConfig config) noexcept
    : config_(config) {}

NetworkNode::~NetworkNode() {
    if (is_initialized_) {
        disable_radio();
    }
}

NetworkNode::NetworkNode(NetworkNode&& other) noexcept
    : config_(other.config_),
      is_initialized_(other.is_initialized_),
      mac_seq_num_(other.mac_seq_num_) {
    other.is_initialized_ = false;
}

NetworkNode& NetworkNode::operator=(NetworkNode&& other) noexcept {
    if (this != &other) {
        if (is_initialized_) {
            disable_radio();
        }
        config_ = other.config_;
        is_initialized_ = other.is_initialized_;
        mac_seq_num_ = other.mac_seq_num_;
        other.is_initialized_ = false;
    }
    return *this;
}

esp_err_t NetworkNode::initialize() noexcept {
    ESP_LOGI(TAG, "Конфігурація трансивера IEEE 802.15.4...");

    esp_err_t ret = esp_ieee802154_enable();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося увімкнути модуль 802.15.4: %s", esp_err_to_name(ret));
        return ret;
    }

    esp_ieee802154_set_channel(config_.channel);
    esp_ieee802154_set_panid(config_.pan_id);
    esp_ieee802154_set_short_address(config_.short_addr);
    esp_ieee802154_set_txpower(config_.tx_power_dbm);

    ESP_LOGI(TAG, "Модуль 802.15.4 готовий: Канал=%u, PAN_ID=0x%04X, Адреса=0x%04X",
             config_.channel, config_.pan_id, config_.short_addr);

    is_initialized_ = true;
    return ESP_OK;
}

std::array<uint8_t, 127> NetworkNode::build_ieee802154_frame(std::span<const uint8_t> payload, uint8_t& out_frame_len) noexcept {
    std::array<uint8_t, 127> frame{};

    // FCF: Data Frame, Ack Request, Intra-PAN, Short Addressing
    uint16_t fcf = 0x8841;
    size_t idx = 0;

    // Перший байт довжини кадру для драйвера ESP32-C6
    idx++;

    // Заголовок FCF
    frame[idx++] = static_cast<uint8_t>(fcf & 0xFF);
    frame[idx++] = static_cast<uint8_t>((fcf >> 8) & 0xFF);

    // Номер послідовності кадру
    frame[idx++] = mac_seq_num_++;

    // PAN ID призначення
    frame[idx++] = static_cast<uint8_t>(config_.pan_id & 0xFF);
    frame[idx++] = static_cast<uint8_t>((config_.pan_id >> 8) & 0xFF);

    // Коротка адреса призначення
    frame[idx++] = static_cast<uint8_t>(config_.dest_addr & 0xFF);
    frame[idx++] = static_cast<uint8_t>((config_.dest_addr >> 8) & 0xFF);

    // Коротка адреса джерела
    frame[idx++] = static_cast<uint8_t>(config_.short_addr & 0xFF);
    frame[idx++] = static_cast<uint8_t>((config_.short_addr >> 8) & 0xFF);

    // Копіювання корисного навантаження
    size_t max_payload = frame.size() - idx - 2;
    size_t copy_bytes = std::min(payload.size(), max_payload);
    std::memcpy(&frame[idx], payload.data(), copy_bytes);
    idx += copy_bytes;

    // Резервування 2 байтів под FCS CRC
    idx += 2;

    frame[0] = static_cast<uint8_t>(idx - 1);
    out_frame_len = static_cast<uint8_t>(idx);

    return frame;
}

esp_err_t NetworkNode::transmit_data(std::span<const uint8_t> payload) noexcept {
    if (!is_initialized_) {
        ESP_LOGE(TAG, "Радіомодуль не ініціалізовано перед передачею");
        return ESP_ERR_INVALID_STATE;
    }

    uint8_t frame_len = 0;
    auto frame_buf = build_ieee802154_frame(payload, frame_len);

    ESP_LOGI(TAG, "Надсилання кадру 802.15.4 (довжина %u байт)...", frame_len);

    esp_err_t ret = esp_ieee802154_transmit(frame_buf.data(), false);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка передачі кадру: %s", esp_err_to_name(ret));
        return ret;
    }

    vTaskDelay(pdMS_TO_TICKS(10));

    ESP_LOGI(TAG, "Пакет успішно відправлено в ефір");
    return ESP_OK;
}

esp_err_t NetworkNode::disable_radio() noexcept {
    if (!is_initialized_) {
        return ESP_OK;
    }

    ESP_LOGI(TAG, "Деактивація бездротового модуля 802.15.4...");
    esp_err_t ret = esp_ieee802154_disable();
    if (ret != ESP_OK) {
        ESP_LOGW(TAG, "Помилка при зупинці радіомодуля: %s", esp_err_to_name(ret));
    }
    is_initialized_ = false;
    return ret;
}

} // namespace iot
