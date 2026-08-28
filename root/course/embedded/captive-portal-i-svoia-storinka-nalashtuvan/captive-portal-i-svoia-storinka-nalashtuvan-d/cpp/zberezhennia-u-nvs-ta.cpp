#include <string_view>
#include <string>
#include "nvs_flash.h"
#include "nvs.h"

namespace embedded::storage {

[[nodiscard]] inline bool saveWifiCredentials(std::string_view ssid, std::string_view pass) noexcept {
    nvs_handle_t handle{};
    if (nvs_open("wifi_cfg", NVS_READWRITE, &handle) != ESP_OK) {
        return false;
    }

    struct NvsGuard {
        nvs_handle_t h;
        ~NvsGuard() { nvs_close(h); }
    } guard{handle};

    std::string s(ssid);
    std::string p(pass);
    nvs_set_str(handle, "ssid", s.c_str());
    nvs_set_str(handle, "password", p.c_str());
    nvs_set_u8(handle, "configured", 1);

    return nvs_commit(handle) == ESP_OK;
}

} // namespace embedded::storage
