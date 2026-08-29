#include "portal/credential_store.hpp"

#include <utility>

#include "esp_log.h"
#include "nvs.h"
#include "nvs_flash.h"

namespace portal::credentials {
namespace {

constexpr const char *kTag = "cfg";
constexpr const char *kNamespace = "wifi_cfg";
constexpr const char *kKeySsid = "ssid";
constexpr const char *kKeyPassword = "password";
constexpr const char *kKeyConfigured = "configured";

/* Власник дескриптора NVS: nvs_close викликається сам на будь-якому виході. */
class NvsHandle {
public:
    static Result<NvsHandle> open(nvs_open_mode_t mode) noexcept
    {
        nvs_handle_t handle{};
        if (const esp_err_t err = nvs_open(kNamespace, mode, &handle); err != ESP_OK) {
            return std::unexpected(err);
        }
        return NvsHandle{handle};
    }

    NvsHandle(const NvsHandle &) = delete;
    NvsHandle &operator=(const NvsHandle &) = delete;

    NvsHandle(NvsHandle &&other) noexcept
        : handle_{std::exchange(other.handle_, 0)} {}

    NvsHandle &operator=(NvsHandle &&other) noexcept
    {
        if (this != &other) {
            close();
            handle_ = std::exchange(other.handle_, 0);
        }
        return *this;
    }

    ~NvsHandle() { close(); }

    [[nodiscard]] nvs_handle_t get() const noexcept { return handle_; }

    [[nodiscard]] Status setString(const char *key, std::string_view value) const noexcept
    {
        /* nvs_set_str чекає на завершальний нуль, якого у view може не бути. */
        const std::string text{value};
        return check(nvs_set_str(handle_, key, text.c_str()));
    }

    [[nodiscard]] Status setFlag(const char *key, std::uint8_t value) const noexcept
    {
        return check(nvs_set_u8(handle_, key, value));
    }

    [[nodiscard]] Status commit() const noexcept { return check(nvs_commit(handle_)); }

    /* Двокрокове читання: спершу довжина, потім самі дані. */
    [[nodiscard]] Result<std::string> getString(const char *key) const noexcept
    {
        std::size_t length = 0;
        if (const esp_err_t err = nvs_get_str(handle_, key, nullptr, &length);
            err != ESP_OK) {
            return std::unexpected(err);
        }

        std::string value(length, '\0');
        if (const esp_err_t err = nvs_get_str(handle_, key, value.data(), &length);
            err != ESP_OK) {
            return std::unexpected(err);
        }

        /* Довжина від NVS враховує завершальний нуль — рядку він не потрібен. */
        if (!value.empty() && value.back() == '\0') {
            value.pop_back();
        }
        return value;
    }

    [[nodiscard]] Result<std::uint8_t> getFlag(const char *key) const noexcept
    {
        std::uint8_t value = 0;
        if (const esp_err_t err = nvs_get_u8(handle_, key, &value); err != ESP_OK) {
            return std::unexpected(err);
        }
        return value;
    }

private:
    explicit NvsHandle(nvs_handle_t handle) noexcept : handle_{handle} {}

    void close() noexcept
    {
        if (handle_ != 0) {
            nvs_close(handle_);
            handle_ = 0;
        }
    }

    nvs_handle_t handle_{};
};

}  // namespace

bool isConfigured() noexcept
{
    const auto nvs = NvsHandle::open(NVS_READONLY);
    if (!nvs) {
        return false;
    }
    const auto flag = nvs->getFlag(kKeyConfigured);
    return flag.has_value() && *flag == 1;
}

Result<Credentials> load() noexcept
{
    auto nvs = NvsHandle::open(NVS_READONLY);
    if (!nvs) {
        return forwardError(nvs);
    }

    const auto flag = nvs->getFlag(kKeyConfigured);
    if (!flag || *flag != 1) {
        return std::unexpected(ESP_ERR_NVS_NOT_FOUND);
    }

    auto ssid = nvs->getString(kKeySsid);
    if (!ssid) {
        return forwardError(ssid);
    }

    auto password = nvs->getString(kKeyPassword);
    if (!password) {
        if (password.error() != ESP_ERR_NVS_NOT_FOUND) {
            return forwardError(password);
        }
        /* Відкрита мережа: ключ пароля просто не заводили. */
        password = std::string{};
    }

    return Credentials{.ssid = std::move(*ssid), .password = std::move(*password)};
}

Status save(std::string_view ssid, std::string_view password) noexcept
{
    if (ssid.empty() || ssid.size() > kSsidMax || password.size() > kPasswordMax) {
        return std::unexpected(ESP_ERR_INVALID_ARG);
    }

    auto nvs = NvsHandle::open(NVS_READWRITE);
    if (!nvs) {
        ESP_LOGE(kTag, "Не вдалося відкрити простір імен NVS: %s",
                 esp_err_to_name(nvs.error()));
        return forwardError(nvs);
    }

    /*
     * Крок 1. Знімаємо ознаку завершеності окремим комітом. З цієї миті
     * будь-яке падіння живлення лишить пристрій у стані «конфігурації
     * немає» — тобто він підніме портал, а не спробує підключитися
     * напівзаписаними даними.
     */
    auto status = nvs->setFlag(kKeyConfigured, 0)
                      .and_then([&] { return nvs->commit(); })
                      /* Крок 2. Кладемо самі поля. */
                      .and_then([&] { return nvs->setString(kKeySsid, ssid); })
                      .and_then([&] { return nvs->setString(kKeyPassword, password); })
                      .and_then([&] { return nvs->commit(); })
                      /* Крок 3. Ознака завершеності — останньою. */
                      .and_then([&] { return nvs->setFlag(kKeyConfigured, 1); })
                      .and_then([&] { return nvs->commit(); });

    if (!status) {
        ESP_LOGE(kTag, "Запис конфігурації обірвався: %s",
                 esp_err_to_name(status.error()));
    } else {
        ESP_LOGI(kTag, "Конфігурацію для мережі \"%.*s\" збережено",
                 static_cast<int>(ssid.size()), ssid.data());
    }

    return status;
}

Status erase() noexcept
{
    auto nvs = NvsHandle::open(NVS_READWRITE);
    if (!nvs) {
        return forwardError(nvs);
    }

    return check(nvs_erase_all(nvs->get())).and_then([&] { return nvs->commit(); });
}

}  // namespace portal::credentials
