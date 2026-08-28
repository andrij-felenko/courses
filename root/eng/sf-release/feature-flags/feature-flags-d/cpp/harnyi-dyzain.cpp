// ГАРНО: Бізнес-сервіс працює з чистим інтерфейсом
class PaymentGateway {
public:
    virtual ~PaymentGateway() = default;
    virtual void charge(double amount) = 0;
    virtual void refund(double amount) = 0;
};

// Маршрутизатор за прапорцем як єдина точка ухвалення рішення
class FeatureFlaggedPaymentGateway : public PaymentGateway {
public:
    FeatureFlaggedPaymentGateway(
        std::shared_ptr<PaymentGateway> legacy_gw,
        std::shared_ptr<PaymentGateway> modern_gw,
        std::shared_ptr<FlagEngine> flags,
        EvaluationContext ctx
    ) : legacy_(legacy_gw), modern_(modern_gw), flags_(flags), ctx_(ctx) {}

    void charge(double amount) override {
        get_active()->charge(amount);
    }

    void refund(double amount) override {
        get_active()->refund(amount);
    }

private:
    PaymentGateway* get_active() {
        return flags_->evaluate("payment-gateway-v2", ctx_).value ? modern_.get() : legacy_.get();
    }

    std::shared_ptr<PaymentGateway> legacy_;
    std::shared_ptr<PaymentGateway> modern_;
    std::shared_ptr<FlagEngine> flags_;
    EvaluationContext ctx_;
};
