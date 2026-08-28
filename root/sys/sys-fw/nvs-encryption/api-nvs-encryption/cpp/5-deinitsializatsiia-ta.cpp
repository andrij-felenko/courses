#include "nvs_flash.h"
#include <string_view>

namespace esp_nvs {

[[nodiscard]] inline esp_err_t deinit_custom_partition(
    std::string_view partition_name) noexcept
{
    return nvs_flash_deinit_partition(partition_name.data());
}

} // namespace esp_nvs
