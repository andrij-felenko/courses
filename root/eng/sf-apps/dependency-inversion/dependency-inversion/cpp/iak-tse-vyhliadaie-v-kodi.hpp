// Деталь ПІДЛАШТОВУЄТЬСЯ під абстракцію верхнього шару
class StripeGateway : public PaymentGateway {
    StripeHttpClient http_;
public:
    ChargeResult charge(const Money& amount, const Card& card) override {
        auto body = toStripeJson(amount, card);
        auto resp = http_.post("https://api.stripe.com/charges", body);
        return { resp.status == 200, resp.errorMessage() };
    }
};
