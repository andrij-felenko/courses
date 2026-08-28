// Абстракція говорить БІЗНЕС-мовою: «списати кошти», а не «зробити POST»
type PaymentGateway interface {
    Charge(amount Money, card Card) ChargeResult
}

// Ядро залежить ЛИШЕ від обіцянки — і не знає, хто її виконає
type PaymentService struct {
    gateway PaymentGateway // посилання на абстракцію
}

func NewPaymentService(g PaymentGateway) *PaymentService {
    return &PaymentService{gateway: g}
}

func (s *PaymentService) Charge(o Order) error {
    r := s.gateway.Charge(o.Total(), o.Card())
    if !r.OK {
        return PaymentFailed{r.Reason}
    }
    return nil
}
