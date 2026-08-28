#include "nvs_flash.h"

namespace esp_nvs {

[[nodiscard]] inline esp_err_t secure_init_default(nvs_sec_cfg_t& cfg) noexcept
{
    return nvs_flash_secure_init(&cfg);
}

} // namespace esp_nvs
