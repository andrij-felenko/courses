// Абстракція говорить БІЗНЕС-мовою: «списати кошти», а не «зробити POST»
struct PaymentGateway {
    virtual ~PaymentGateway() = default;
    virtual ChargeResult charge(const Money& amount, const Card& card) = 0;
};

// Ядро залежить ЛИШЕ від обіцянки — і не знає, хто її виконає
class PaymentService {
    PaymentGateway& gateway_;           // посилання на абстракцію
public:
    explicit PaymentService(PaymentGateway& g) : gateway_(g) {}

    void charge(const Order& o) {
        auto r = gateway_.charge(o.total(), o.card());
        if (!r.ok) throw PaymentFailed(r.reason);
    }
};
