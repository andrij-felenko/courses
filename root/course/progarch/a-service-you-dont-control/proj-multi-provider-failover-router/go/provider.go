package main

import (
	"context"
	"time"
)

// Request — уніфікована модель запиту до стороннього провайдера.
type Request struct {
	ID             string    // Унікальний ідентифікатор операції
	Method         string    // HTTP-метод або тип операції (GET, POST тощо)
	Endpoint       string    // Шлях до віддаленого ресурсу
	Payload        []byte    // Тіло запиту
	IdempotencyKey string    // Ключ ідемпотентності для мутуючих запитів
	IsIdempotent   bool      // Чи гарантовано операція є безпечною для повтору
	CreatedAt      time.Time // Час створення запиту
}

// Response — уніфікована відповідь зовнішньої служби.
type Response struct {
	StatusCode int           // Код відповіді (200, 500, 503 тощо)
	Body       []byte        // Дані відповіді
	Duration   time.Duration // Фактична тривалість обробки запиту
	ProviderID string        // Ідентифікатор провайдера, що виконав запит
}

// Provider — контракт взаємодії зі стороннім сервісом.
type Provider interface {
	// ID повертає унікальне ім'я провайдера (наприклад, "stripe", "adyen").
	ID() string
	// Execute виконує виклик до зовнішнього API з урахуванням дедлайну контексту.
	Execute(ctx context.Context, req Request) (Response, error)
}\n
