#include <string_view>
#include <expected>
#include <chrono>
#include <regex>
#include <memory>
#include <iostream>
#include "user_profile.pb.h"

namespace billing::domain {

// Коди помилок валідації бізнес-правил профілю
enum class ValidationError {
    InvalidEmailFormat,
    NegativeBalanceNotAllowed,
    AccountSuspended,
    InvalidAccountId
};

class ProfileDomainService {
public:
    // Перевірка інваріантів домену перед збереженням чи мутацією
    [[nodiscard]] std::expected<void, ValidationError> validate_profile(
        const billing::v1::UserProfile& profile
    ) const noexcept {
        if (profile.account_id() == 0) {
            return std::unexpected(ValidationError::InvalidAccountId);
        }

        if (profile.is_suspended()) {
            return std::unexpected(ValidationError::AccountSuspended);
        }

        // Перевірка формату адреси електронної пошти за стандартом
        static const std::regex email_pattern(
            R"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        );
        if (!std::regex_match(profile.email(), email_pattern)) {
            return std::unexpected(ValidationError::InvalidEmailFormat);
        }

        // Баланс не може бути від’ємним для базових акаунтів
        if (profile.balance_cents() < 0) {
            return std::unexpected(ValidationError::NegativeBalanceNotAllowed);
        }

        return {};
    }

    // Застосування транзакційного списання коштів з балансу
    [[nodiscard]] std::expected<billing::v1::UserProfile, ValidationError> apply_charge(
        billing::v1::UserProfile current,
        int64_t charge_amount_cents
    ) const {
        auto check = validate_profile(current);
        if (!check) {
            return std::unexpected(check.error());
        }

        if (current.balance_cents() < charge_amount_cents) {
            return std::unexpected(ValidationError::NegativeBalanceNotAllowed);
        }

        // Безпечна модифікація через згенеровані аксесори
        current.set_balance_cents(current.balance_cents() - charge_amount_cents);

        // Оновлення мітки часу останньої мутації
        const auto now_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()
        ).count();
        current.set_updated_at_ms(now_ms);

        return current;
    }
};

} // namespace billing::domain
