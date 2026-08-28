// Ядро прибите до конкретного HTTP-клієнта: стрілка «важливе → дрібне»
#include "StripeHttpClient.h"          // деталь протекла у файл із логікою

class PaymentService {
    StripeHttpClient http_;            // ядро ТРИМАЄ конкретну деталь
public:
    void charge(const Order& o) {
        auto body = buildStripeJson(o); // логіка знає формат саме Stripe
        http_.post("https://api.stripe.com/charges", body);
    }
};
