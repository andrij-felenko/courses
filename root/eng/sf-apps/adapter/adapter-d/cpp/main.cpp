#include <cctype>
#include <cmath>
#include <string>

static std::string toLower(std::string s) {
    for (char& c : s) c = (char)std::tolower((unsigned char)c);
    return s;
}

struct PaymentGateway {                       // Ціль
    virtual std::string charge(double amount, const std::string& cur) = 0;
    virtual ~PaymentGateway() = default;
};

class StripeClient {                          // Адаптований (чужий), із ВІРТУАЛЬНИМ методом
public:
    virtual std::string createCharge(long minor, const std::string& cur) {
        return "ch_live";                     // справжній виклик до Stripe
    }
    virtual ~StripeClient() = default;
};

// КЛАСОВИЙ адаптер: Ціль — ПУБЛІЧНО (is-a), Адаптований — ПРИВАТНО (implemented-in-terms-of)
class StripeAdapter : public PaymentGateway, private StripeClient {
public:
    std::string charge(double amount, const std::string& cur) override {
        return createCharge(std::lround(amount * 100), toLower(cur));  // метод предка — напряму
    }
private:
    // ЄДИНА справжня перевага класової форми: перевизначити поведінку адаптованого
    std::string createCharge(long minor, const std::string& cur) override {
        return "test_" + StripeClient::createCharge(minor, cur);       // напр., позначити тестовим
    }
};
