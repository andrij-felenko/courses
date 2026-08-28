// Ядро прибите до конкретного HTTP-клієнта: стрілка «важливе → дрібне»
import "example.com/stripe" // деталь протекла у пакет із логікою

type PaymentService struct {
    http stripe.HttpClient // ядро ТРИМАЄ конкретну деталь
}

func (s *PaymentService) Charge(o Order) {
    body := buildStripeJSON(o) // логіка знає формат саме Stripe
    s.http.Post("https://api.stripe.com/charges", body)
}
