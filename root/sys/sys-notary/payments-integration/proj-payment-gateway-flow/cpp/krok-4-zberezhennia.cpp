#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <format>

struct SetupCardResult {
    std::string setup_intent_id;
    std::string status;
};

class SubscriptionSetupService {
private:
    std::string api_key_;
    std::string base_url_;

public:
    explicit SubscriptionSetupService(std::string_view api_key,
                                    std::string_view base_url = "https://api.stripe.com/v1")
        : api_key_(api_key), base_url_(base_url) {}

    [[nodiscard]] std::expected<SetupCardResult, std::string>
    attach_payment_method(std::string_view customer_id, std::string_view payment_method_id) const {
        if (customer_id.empty() || payment_method_id.empty()) {
            return std::unexpected("Ідентифікатори клієнта та методу оплати не можуть бути порожніми");
        }

        // Імітація успішного отримання мандата off-session
        return SetupCardResult{
            .setup_intent_id = std::format("seti_{}_{}", customer_id, payment_method_id),
            .status = "succeeded"
        };
    }
};
