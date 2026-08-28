#include <iostream>
#include <iomanip>
#include <span>
#include <array>
#include <string_view>
#include <cstring>
#include "esp_log.h"
#include "esp_flash_encrypt.h"
#include "esp_partition.h"

namespace Security {

class FlashAuditor {
public:
    static constexpr std::string_view Tag = "SEC_AUDITOR_CPP";
    static constexpr size_t BlockSize = 32;

    struct EncryptionReport {
        bool is_enabled{false};
        esp_flash_enc_mode_t mode{ESP_FLASH_ENC_MODE_DEVELOPMENT};
        bool is_production_ready{false};
    };

    [[nodiscard]] static auto InspectSystem() -> EncryptionReport {
        EncryptionReport report{};
        report.is_enabled = esp_flash_encryption_enabled();

        if (!report.is_enabled) {
            ESP_LOGW(Tag.data(), "Flash encryption is disabled!");
            return report;
        }

        report.mode = esp_flash_encryption_get_mode();
        report.is_production_ready = (report.mode == ESP_FLASH_ENC_MODE_RELEASE);

        if (report.is_production_ready) {
            ESP_LOGI(Tag.data(), "Running in hardened RELEASE mode.");
        } else {
            ESP_LOGW(Tag.data(), "Device is in DEVELOPMENT mode. Keys can be overwritten!");
        }

        return report;
    }

    static auto VerifyPartitionEncryption(std::string_view partition_name) -> bool {
        const esp_partition_t* partition = esp_partition_find_first(
            ESP_PARTITION_TYPE_DATA,
            ESP_PARTITION_SUBTYPE_ANY,
            partition_name.data()
        );

        if (partition == nullptr) {
            ESP_LOGE(Tag.data(), "Partition not found: %.*s", static_cast<int>(partition_name.size()), partition_name.data());
            return false;
        }

        if (!partition->encrypted) {
            ESP_LOGW(Tag.data(), "Partition '%.*s' is NOT marked as encrypted.", static_cast<int>(partition_name.size()), partition_name.data());
            return false;
        }

        std::array<uint8_t, BlockSize> plain_data{};
        std::array<uint8_t, BlockSize> raw_data{};

        auto err_read = esp_partition_read(partition, 0, plain_data.data(), plain_data.size());
        auto err_raw  = esp_partition_read_raw(partition, 0, raw_data.data(), raw_data.size());

        if (err_read != ESP_OK || err_raw != ESP_OK) {
            ESP_LOGE(Tag.data(), "Failed to read partition data for cryptographic audit.");
            return false;
        }

        bool are_different = (plain_data != raw_data);
        if (are_different) {
            ESP_LOGI(Tag.data(), "Integrity confirmed: Physical Flash storage holds ciphertext.");
        }
        return are_different;
    }

    static auto WriteEncryptedBlock(
        const esp_partition_t* partition,
        size_t offset,
        std::span<const uint8_t> data
    ) -> esp_err_t {
        if (partition == nullptr || data.empty()) {
            return ESP_ERR_INVALID_ARG;
        }

        if ((data.size() % BlockSize != 0) || (offset % BlockSize != 0)) {
            ESP_LOGE(Tag.data(), "Alignment error: data size and offset must be multiples of 32 bytes.");
            return ESP_ERR_INVALID_ARG;
        }

        esp_err_t result = esp_partition_write(partition, offset, data.data(), data.size());
        if (result != ESP_OK) {
            ESP_LOGE(Tag.data(), "Flash write failed with error code: 0x%x", result);
        }
        return result;
    }
};

} // namespace Security

extern "C" void app_main_cpp()
{
    auto report = Security::FlashAuditor::InspectSystem();
    if (report.is_enabled) {
        Security::FlashAuditor::VerifyPartitionEncryption("storage");
    }
}
