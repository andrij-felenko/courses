#include "nvs_flash.h"

namespace esp_nvs {

[[nodiscard]] inline esp_err_t generate_security_keys(
    const esp_partition_t* partition,
    nvs_sec_cfg_t& cfg) noexcept
{
    return nvs_flash_generate_keys(partition, &cfg);
}

} // namespace esp_nvs
