// kill_switch_contract.hpp - C++20 контракт кілл-світча
#include <string_view>
#include <expected>
#include <chrono>

enum class FeatureFlagError {
    ProviderUnavailable,
    KeyNotFound,
    Timeout
};

class IKillSwitchProvider {
public:
    virtual ~IKillSwitchProvider() = default;

    // Атомарна перевірка стану прапора (час виконання < 1 мкс)
    [[nodiscard]] virtual bool is_feature_enabled(std::string_view flag_key, bool default_value = false) noexcept = 0;

    // Примусова атомарна деактивація прапора контролером відкату
    virtual std::expected<void, FeatureFlagError> emergency_disable_flag(std::string_view flag_key) = 0;
};
