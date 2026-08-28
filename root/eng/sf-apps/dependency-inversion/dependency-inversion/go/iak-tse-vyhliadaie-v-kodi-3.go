// Деталь ПІДЛАШТОВУЄТЬСЯ під абстракцію верхнього шару
type StripeGateway struct {
    http stripe.HttpClient
}

func (g *StripeGateway) Charge(amount Money, card Card) ChargeResult {
    body := toStripeJSON(amount, card)
    resp := g.http.Post("https://api.stripe.com/charges", body)
    return ChargeResult{OK: resp.Status == 200, Reason: resp.ErrorMessage()}
}
