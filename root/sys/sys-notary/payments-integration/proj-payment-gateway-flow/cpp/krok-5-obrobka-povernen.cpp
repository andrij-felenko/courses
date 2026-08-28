#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <format>

struct RefundResult {
    std::string refund_id;
    std::string status;
};

class PaymentRefundService {
private:
    std::string api_key_;
    std::string base_url_;

public:
    explicit PaymentRefundService(std::string_view api_key,
                                 std::string_view base_url = "https://api.stripe.com/v1")
        : api_key_(api_key), base_url_(base_url) {}

    [[nodiscard]] std::expected<RefundResult, std::string>
    process_refund(std::string_view payment_intent_id, std::optional<int64_t> amount_cents = std::nullopt) const {
        if (payment_intent_id.empty()) {
            return std::unexpected("Ідентифікатор наміру не може бути порожнім");
        }

        return RefundResult{
            .refund_id = std::format("re_{}", payment_intent_id),
            .status = "succeeded"
        };
    }
};
