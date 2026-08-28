// Ціль — інтерфейс, який очікує наш код
struct PaymentGateway {
    virtual std::string charge(double amountUAH, const std::string& currency) = 0;
    virtual ~PaymentGateway() = default;
};

// Адаптований — чужий клас із власним методом
struct StripeClient {
    std::string createCharge(long amountInCents, const std::string& currency) {
        return "ch_123";
    }
};

// КЛАСОВИЙ адаптер: успадковує обидва — і ціль, і адаптованого
class StripeAdapter : public PaymentGateway, private StripeClient {
public:
    std::string charge(double amountUAH, const std::string& currency) override {
        // createCharge доступний напряму — він успадкований, поля нема
        return createCharge(std::lround(amountUAH * 100), toLower(currency));
    }
};
