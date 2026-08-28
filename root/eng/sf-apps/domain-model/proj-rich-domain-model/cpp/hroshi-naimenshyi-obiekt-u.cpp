#include <string>
#include <vector>
#include <optional>
#include <cstdint>
#include <stdexcept>

struct DomainError : std::runtime_error {
    using std::runtime_error::runtime_error;
};

using Cents = std::int64_t;                       // копійки цілим числом, не дріб

class Money {
public:
    // єдині двері всередину — з вартовим: гроші не бувають від'ємні
    static Money of(Cents cents, std::string currency) {
        if (cents < 0) throw DomainError("гроші не бувають від'ємні");
        return Money(cents, std::move(currency));
    }
    static Money zero(std::string currency) { return Money(0, std::move(currency)); }

    Money add(const Money& o) const {
        requireSameCurrency(o);
        return Money(cents_ + o.cents_, currency_);        // новий об'єкт, старі не змінені
    }
    Money times(int qty) const {
        if (qty < 0) throw DomainError("кількість не буває від'ємна");
        return Money(cents_ * qty, currency_);
    }
    Money withDiscountPercent(int pct) const {
        if (pct < 0 || pct > 100) throw DomainError("відсоток поза межами 0..100");
        return Money(cents_ - cents_ * pct / 100, currency_);
    }

    bool operator==(const Money& o) const {                // рівність за ВМІСТОМ — рідна мові
        return cents_ == o.cents_ && currency_ == o.currency_;
    }
    Cents cents() const { return cents_; }
    const std::string& currency() const { return currency_; }

private:
    Money(Cents cents, std::string currency)               // конструктор закритий
        : cents_(cents), currency_(std::move(currency)) {}
    void requireSameCurrency(const Money& o) const {
        if (currency_ != o.currency_) throw DomainError("не можна складати різні валюти");
    }
    Cents cents_;
    std::string currency_;
};
