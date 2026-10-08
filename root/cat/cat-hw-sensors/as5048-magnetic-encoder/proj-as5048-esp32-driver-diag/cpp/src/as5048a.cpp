#include "as5048a.hpp"
#include "esp_log.h"
#include <cstring>

static const char* TAG = "AS5048A";
static const char* NVS_NAMESPACE = "as5048_storage";
static const char* NVS_KEY_ZERO = "zero_offset";

namespace encoder {

AS5048A::AS5048A(spi_host_device_t spi_host, gpio_num_t cs_pin)
    : spi_host_(spi_host), cs_pin_(cs_pin) {}

AS5048A::~AS5048A() {
    if (spi_device_ != nullptr) {
        spi_bus_remove_device(spi_device_);
    }
}

esp_err_t AS5048A::begin() {
    spi_device_interface_config_t devcfg = {};
    devcfg.clock_speed_hz = 5 * 1000 * 1000; // 5 МГц (AS5048A підтримує до 10 МГц)
    devcfg.mode = 1;                         // SPI Mode 1 (CPOL=0, CPHA=1)
    devcfg.spics_io_num = cs_pin_;
    devcfg.queue_size = 1;
    devcfg.flags = SPI_DEVICE_NO_DUMMY;

    esp_err_t ret = spi_bus_add_device(spi_host_, &devcfg, &spi_device_);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка додавання SPI пристрою: %s", esp_err_to_name(ret));
        return ret;
    }

    // Завантажуємо нульовий зсув з NVS флеш-пам'яті
    ret = load_zero_offset_from_nvs();
    if (ret != ESP_OK && ret != ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGW(TAG, "Попередження при читанні NVS: %s", esp_err_to_name(ret));
    }

    ESP_LOGI(TAG, "Драйвер AS5048A ініціалізовано. Поточний zero_offset: %u", zero_offset_);
    return ESP_OK;
}

bool AS5048A::is_even_parity(uint16_t val) {
    // Обчислення підсумовуванням бітів (parity check):
    // Результат true (1), якщо сумарна кількість одиниць парна
    uint16_t count = 0;
    for (uint16_t temp = val; temp != 0; temp >>= 1) {
        count += (temp & 1);
    }
    return (count % 2) == 0;
}

uint16_t AS5048A::build_read_command(Register reg) {
    // Структура кадру команди AS5048A (16 біт):
    // Bit 15: Parity (Парність)
    // Bit 14: Read = 1, Write = 0
    // Bits 13..0: Address (14 біт)
    uint16_t cmd = (1u << 14) | (static_cast<uint16_t>(reg) & 0x3FFF);
    
    // Обчислюємо біт парності для бітів 14..0
    uint16_t ones_count = 0;
    for (uint16_t temp = cmd; temp != 0; temp >>= 1) {
        ones_count += (temp & 1);
    }
    
    // Якщо кількість одиниць непарна (ones_count % 2 != 0), додаємо 1 у Bit 15,
    // щоб загальна кількість одиниць у 16-бітному кадрі стала ПАРНОЮ.
    if ((ones_count % 2) != 0) {
        cmd |= (1u << 15);
    }
    
    return cmd;
}

uint16_t AS5048A::spi_transfer16(uint16_t tx_word) {
    spi_transaction_t trans = {};
    trans.flags = SPI_TRANS_USE_TXDATA | SPI_TRANS_USE_RXDATA;
    trans.length = 16; // 16 біт
    
    // SPI передає старшим байтом вперед (MSB First)
    trans.tx_data[0] = static_cast<uint8_t>((tx_word >> 8) & 0xFF);
    trans.tx_data[1] = static_cast<uint8_t>(tx_word & 0xFF);

    esp_err_t ret = spi_device_polling_transmit(spi_device_, &trans);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка передачі SPI: %s", esp_err_to_name(ret));
        return 0;
    }

    uint16_t rx_word = (static_cast<uint16_t>(trans.rx_data[0]) << 8) | trans.rx_data[1];
    return rx_word;
}

bool AS5048A::read_angle_pipelined(uint16_t& raw_angle) {
    const uint16_t read_angle_cmd = build_read_command(Register::Angle);

    if (!pipelined_active_) {
        // Прокачуємо конвеєр: перша транзакція надсилає запит ANGLE
        spi_transfer16(read_angle_cmd);
        pipelined_active_ = true;
    }

    // Друга транзакція надсилає наступний запит ANGLE і повертає результат попереднього
    uint16_t rx_word = spi_transfer16(read_angle_cmd);

    // Перевірка парності отриманого кадру (загальна кількість бітів мусить бути парною)
    if (!is_even_parity(rx_word)) {
        ESP_LOGE(TAG, "Помилка парності в SPI-кадрі кута: 0x%04X", rx_word);
        pipelined_active_ = false;
        return false;
    }

    // Bit 14: Error Flag (EF)
    if ((rx_word & (1u << 14)) != 0) {
        ESP_LOGW(TAG, "Давач встановив прапор помилки EF у кадрі кута: 0x%04X", rx_word);
        pipelined_active_ = false;
        return false;
    }

    // Bits 13..0: 14-бітне значення кута
    raw_angle = rx_word & 0x3FFF;
    return true;
}

bool AS5048A::read_angle_degrees(float& degrees) {
    uint16_t raw_angle = 0;
    if (!read_angle_pipelined(raw_angle)) {
        return false;
    }

    // Обчислення кута з урахуванням калібрувального зміщення нуля
    uint16_t corrected_raw = (raw_angle + K_MAX_ANGLE_RAW - zero_offset_) % K_MAX_ANGLE_RAW;
    degrees = (static_cast<float>(corrected_raw) * 360.0f) / static_cast<float>(K_MAX_ANGLE_RAW);
    return true;
}

bool AS5048A::read_diagnostics(DiagnosticStatus& status) {
    // Перериваємо поточну конвеєрну послідовність
    pipelined_active_ = false;

    // Крок 1: надсилаємо команду READ DIAGNOSTICS_AGC (0x3FFE)
    uint16_t diag_cmd = build_read_command(Register::DiagnosticsAgc);
    spi_transfer16(diag_cmd);

    // Крок 2: надсилаємо NOP, щоб отримати результат виконання команди DIAGNOSTICS_AGC
    uint16_t nop_cmd = build_read_command(Register::Nop);
    uint16_t rx_word = spi_transfer16(nop_cmd);

    status = {};
    if (!is_even_parity(rx_word)) {
        status.parity_error = true;
        ESP_LOGE(TAG, "Помилка парності при зчитуванні діагностики: 0x%04X", rx_word);
        return false;
    }

    status.hardware_error = (rx_word & (1u << 14)) != 0;

    // Маска даних (14 біт):
    // Bits 0..7: AGC (Automatic Gain Control)
    // Bit 8: OCF (Offset Compensation Finished)
    // Bit 9: COF (CORDIC Overflow)
    // Bit 10: COMP_LOW (Магнітне поле заслабке)
    // Bit 11: COMP_HIGH (Магнітне поле занадто сильне)
    uint16_t data = rx_word & 0x3FFF;
    status.agc       = static_cast<uint8_t>(data & 0xFF);
    status.ocf       = (data & (1u << 8)) != 0;
    status.cof       = (data & (1u << 9)) != 0;
    status.comp_low  = (data & (1u << 10)) != 0;
    status.comp_high = (data & (1u << 11)) != 0;

    return true;
}

bool AS5048A::clear_errors(ErrorFlags& errors) {
    pipelined_active_ = false;

    // Крок 1: Запит читання регістру Clear Error (0x0001)
    uint16_t clear_cmd = build_read_command(Register::ClearError);
    spi_transfer16(clear_cmd);

    // Крок 2: NOP для отримання даних прапорців помилок
    uint16_t nop_cmd = build_read_command(Register::Nop);
    uint16_t rx_word = spi_transfer16(nop_cmd);

    errors = {};
    if (!is_even_parity(rx_word)) {
        errors.parity_error = true;
        return false;
    }

    uint16_t data = rx_word & 0x3FFF;
    errors.framing_error   = (data & (1u << 0)) != 0;
    errors.command_invalid = (data & (1u << 1)) != 0;
    errors.parity_error    = (data & (1u << 2)) != 0;

    return true;
}

esp_err_t AS5048A::calibrate_zero_position() {
    uint16_t current_raw = 0;
    // Тимчасово зчитуємо 2 рази для скидання конвеєра та надійного виміру
    if (!read_angle_pipelined(current_raw) || !read_angle_pipelined(current_raw)) {
        ESP_LOGE(TAG, "Не вдалося зчитати поточний кут для калібрування");
        return ESP_FAIL;
    }

    return set_zero_offset(current_raw, true);
}

esp_err_t AS5048A::set_zero_offset(uint16_t offset, bool save_to_nvs) {
    zero_offset_ = offset % K_MAX_ANGLE_RAW;
    ESP_LOGI(TAG, "Встановлено нове нульове зміщення: %u", zero_offset_);

    if (save_to_nvs) {
        return save_zero_offset_to_nvs(zero_offset_);
    }
    return ESP_OK;
}

esp_err_t AS5048A::load_zero_offset_from_nvs() {
    nvs_handle_t nvs_h;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READONLY, &nvs_h);
    if (err != ESP_OK) {
        return err;
    }

    uint16_t loaded_offset = 0;
    err = nvs_get_u16(nvs_h, NVS_KEY_ZERO, &loaded_offset);
    nvs_close(nvs_h);

    if (err == ESP_OK) {
        zero_offset_ = loaded_offset % K_MAX_ANGLE_RAW;
        ESP_LOGI(TAG, "Успішно завантажено zero_offset з NVS: %u", zero_offset_);
    }
    return err;
}

esp_err_t AS5048A::save_zero_offset_to_nvs(uint16_t offset) {
    nvs_handle_t nvs_h;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &nvs_h);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося відкрити NVS для запису: %s", esp_err_to_name(err));
        return err;
    }

    err = nvs_set_u16(nvs_h, NVS_KEY_ZERO, offset);
    if (err == ESP_OK) {
        err = nvs_commit(nvs_h);
        if (err == ESP_OK) {
            ESP_LOGI(TAG, "Калібрувальне зміщення %u збережено у флеш-пам'ять NVS", offset);
        } else {
            ESP_LOGE(TAG, "Помилка фіксації nvs_commit: %s", esp_err_to_name(err));
        }
    } else {
        ESP_LOGE(TAG, "Помилка запису в NVS: %s", esp_err_to_name(err));
    }

    nvs_close(nvs_h);
    return err;
}

} // namespace encoder
