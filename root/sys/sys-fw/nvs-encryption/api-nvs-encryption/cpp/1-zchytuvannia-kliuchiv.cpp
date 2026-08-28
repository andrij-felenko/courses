#include "nvs_flash.h"
#include <expected>
#include <system_error>

namespace esp_nvs {

[[nodiscard]] inline esp_err_t read_security_config(
    const esp_partition_t* partition,
    nvs_sec_cfg_t& cfg) noexcept
{
    return nvs_flash_read_security_cfg(partition, &cfg);
}

} // namespace esp_nvs
