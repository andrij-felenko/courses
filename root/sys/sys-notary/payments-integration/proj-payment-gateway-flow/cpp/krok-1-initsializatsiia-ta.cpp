#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <cstdint>
#include <format>
#include <sstream>

struct CreatePaymentParams {
    std::string order_id;
    int64_t amount_cents;
    std::string currency;
    std::string payment_method_id;
    std::string customer_id;
};

enum class PaymentIntentStatus {
    RequiresPaymentMethod,
    RequiresConfirmation,
    RequiresAction,
    Processing,
    RequiresCapture,
    Succeeded,
    Canceled,
    Failed,
    Unknown
};

struct PaymentIntentResult {
    std::string intent_id;
    PaymentIntentStatus status;
    std::optional<std::string> client_secret;
    bool requires_action;
};

class PaymentGatewayService {
private:
    std::string api_key_;
    std::string base_url_;

public:
    explicit PaymentGatewayService(std::string_view api_key,
                                  std::string_view base_url = "https://api.stripe.com/v1")
        : api_key_(api_key), base_url_(base_url) {}

    [[nodiscard]] std::string make_idempotency_key(const CreatePaymentParams& params) const {
        return std::format("checkout_{}_{}", params.order_id, params.amount_cents);
    }

    [[nodiscard]] std::expected<PaymentIntentResult, std::string>
    process_checkout(const CreatePaymentParams& params) const {
        const std::string idem_key = make_idempotency_key(params);

        if (params.amount_cents <= 0) {
            return std::unexpected("Сума списання повинна бути додатною");
        }

        // Імітація обробки відповіді шлюзу у разі потреби 3DS автентифікації
        PaymentIntentResult result{
            .intent_id = "pi_mock_99182312",
            .status = PaymentIntentStatus::RequiresAction,
            .client_secret = "pi_mock_99182312_secret_test",
            .requires_action = true
        };

        return result;
    }
};
