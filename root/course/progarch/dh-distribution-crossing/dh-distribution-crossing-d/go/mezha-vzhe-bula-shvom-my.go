// Порт — та сама форма, що й у гексагоні v2. Логіка хаба знає лише його.
type CloudLink interface {
	Send(ctx context.Context, cmd Command) (Result, error)
}

// Адаптер v2: сусід у тому ж процесі. Дві долі — значення або помилка.
type InProcessCloud struct{ cloud *Cloud }
func (c InProcessCloud) Send(ctx context.Context, cmd Command) (Result, error) {
	return c.cloud.Handle(cmd) // все-або-нічого
}

// Адаптер за межею машини: та сама форма, але за нею — мережа.
// Уся чесність зібрана ТУТ, логіка над портом її не бачить.
type NetworkCloud struct{ http *Client }
func (c NetworkCloud) Send(ctx context.Context, cmd Command) (Result, error) {
	ctx, cancel := context.WithTimeout(ctx, 10*time.Second) // бюджет часу
	defer cancel()
	return withRetries(ctx, func() (Result, error) {         // повтор з відступом
		return c.http.Post(ctx, "/cmd", cmd, cmd.ID)         // ключ = cmd.ID
	})
}
