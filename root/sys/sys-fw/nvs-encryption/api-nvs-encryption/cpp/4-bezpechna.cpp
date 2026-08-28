#include "nvs_flash.h"
#include <string_view>

namespace esp_nvs {

[[nodiscard]] inline esp_err_t secure_init_custom_partition(
    std::string_view partition_name,
    nvs_sec_cfg_t& cfg) noexcept
{
    return nvs_flash_secure_init_partition(partition_name.data(), &cfg);
}

} // namespace esp_nvs
