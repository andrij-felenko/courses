package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"
)

// ContractBuilder — конструктор контракту на базі мок-сервера httptest.Server,
// який фіксує поведінкові очікування клієнта замовника та експортує фінальну JSON-специфікацію.
type ContractBuilder struct {
	mu           sync.Mutex
	consumer     string
	provider     string
	version      string
	interactions []Interaction
	current      *Interaction
	server       *httptest.Server
}

// NewContractBuilder створює новий екземпляр будівельника контракту.
func NewContractBuilder(consumer, provider, version string) *ContractBuilder {
	return &ContractBuilder{
		consumer:     consumer,
		provider:     provider,
		version:      version,
		interactions: make([]Interaction, 0),
	}
}

// Given фіксує передумову на боці провайдера (Provider State).
func (b *ContractBuilder) Given(state string) *ContractBuilder {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.current = &Interaction{
		ProviderState: state,
	}
	return b
}

// UponReceiving описує дію чи подію, що ініціює взаємодію.
func (b *ContractBuilder) UponReceiving(description string) *ContractBuilder {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.current == nil {
		b.current = &Interaction{}
	}
	b.current.Description = description
	return b
}

// WithRequest задає параметри очікуваного HTTP-запиту від споживача.
func (b *ContractBuilder) WithRequest(method, path string, headers map[string]string, body any) *ContractBuilder {
	b.mu.Lock()
	defer b.mu.Unlock()
	normBody, _ := NormalizeJSON(body)
	b.current.Request = RequestExpectation{
		Method:  method,
		Path:    path,
		Headers: headers,
		Body:    normBody,
	}
	return b
}

// WillRespondWith задає гарантовану відповідь, яку мок поверне споживачеві, та зберігає взаємодію.
func (b *ContractBuilder) WillRespondWith(status int, headers map[string]string, body any) *ContractBuilder {
	b.mu.Lock()
	defer b.mu.Unlock()
	normBody, _ := NormalizeJSON(body)
	b.current.Response = ResponseExpectation{
		Status:  status,
		Headers: headers,
		Body:    normBody,
	}
	b.interactions = append(b.interactions, *b.current)
	b.current = nil
	return b
}

// Start запускає mock-сервер httptest для обслуговування запитів під час виконання тестів замовника.
func (b *ContractBuilder) Start() string {
	b.mu.Lock()
	defer b.mu.Unlock()

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		b.mu.Lock()
		defer b.mu.Unlock()

		// Пошук зареєстрованої взаємодії за методом і шляхом
		for _, interaction := range b.interactions {
			if r.Method == interaction.Request.Method && r.URL.Path == interaction.Request.Path {
				for hKey, hVal := range interaction.Response.Headers {
					w.Header().Set(hKey, hVal)
				}
				w.WriteHeader(interaction.Response.Status)
				if interaction.Response.Body != nil {
					respBytes, _ := json.Marshal(interaction.Response.Body)
					_, _ = w.Write(respBytes)
				}
				return
			}
		}

		http.Error(w, fmt.Sprintf("мок-сервер: неочікуваний запит %s %s", r.Method, r.URL.Path), http.StatusNotFound)
	})

	b.server = httptest.NewServer(handler)
	return b.server.URL
}

// Close зупиняє вбудований тестовий сервер.
func (b *ContractBuilder) Close() {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.server != nil {
		b.server.Close()
	}
}

// Build створює остаточний об'єкт контракту.
func (b *ContractBuilder) Build() *Contract {
	b.mu.Lock()
	defer b.mu.Unlock()
	contract := NewContract(b.consumer, b.provider, b.version)
	contract.Interactions = append(contract.Interactions, b.interactions...)
	return contract
}

// Export серіалізує записаний контракт у цільовий JSON-файл.
func (b *ContractBuilder) Export(filepath string) error {
	contract := b.Build()
	return contract.SaveToFile(filepath)
}

// TestConsumerContractGeneration перевіряє поведінку клієнта замовника та генерує артефакт контракту.
func TestConsumerContractGeneration(t *testing.T) {
	builder := NewContractBuilder("BillingService", "OrdersProvider", "1.0.0")

	// 1. Очікування: Створення замовлення
	builder.Given("сховище замовлень готове до запису").
		UponReceiving("запит на створення нового замовлення на послугу").
		WithRequest(http.MethodPost, "/orders", map[string]string{
			"Content-Type": "application/json",
		}, CreateOrderRequest{
			CustomerName: "ТОВ Рога і Копита",
			Amount:       1500.50,
			Currency:     "UAH",
		}).
		WillRespondWith(http.StatusCreated, map[string]string{
			"Content-Type": "application/json",
		}, Order{
			ID:           "ord-101",
			CustomerName: "ТОВ Рога і Копита",
			Amount:       1500.50,
			Currency:     "UAH",
			Status:       "PENDING",
		})

	// 2. Очікування: Отримання замовлення за ідентифікатором
	builder.Given("замовлення ord-101 існує в системі підрядника").
		UponReceiving("запит на отримання деталей замовлення ord-101").
		WithRequest(http.MethodGet, "/orders/ord-101", nil, nil).
		WillRespondWith(http.StatusOK, map[string]string{
			"Content-Type": "application/json",
		}, Order{
			ID:           "ord-101",
			CustomerName: "ТОВ Рога і Копита",
			Amount:       1500.50,
			Currency:     "UAH",
			Status:       "PENDING",
		})

	mockURL := builder.Start()
	defer builder.Close()

	client := NewConsumerClient(mockURL, 2*time.Second)
	ctx := context.Background()

	// Тестування сценарію створення замовлення
	t.Run("CreateOrder_Success", func(t *testing.T) {
		order, err := client.CreateOrder(ctx, CreateOrderRequest{
			CustomerName: "ТОВ Рога і Копита",
			Amount:       1500.50,
			Currency:     "UAH",
		})
		if err != nil {
			t.Fatalf("неочікувана помилка виконання CreateOrder: %v", err)
		}
		if order.ID != "ord-101" {
			t.Errorf("очікувався ID 'ord-101', отримано '%s'", order.ID)
		}
		if order.Status != "PENDING" {
			t.Errorf("очікувався статус 'PENDING', отримано '%s'", order.Status)
		}
	})

	// Тестування сценарію отримання замовлення
	t.Run("GetOrder_Success", func(t *testing.T) {
		order, err := client.GetOrder(ctx, "ord-101")
		if err != nil {
			t.Fatalf("неочікувана помилка виконання GetOrder: %v", err)
		}
		if order.CustomerName != "ТОВ Рога і Копита" {
			t.Errorf("очікувався замовник 'ТОВ Рога і Копита', отримано '%s'", order.CustomerName)
		}
		if order.Amount != 1500.50 {
			t.Errorf("очікувалась сума 1500.50, отримано %f", order.Amount)
		}
	})

	// Експорт перевіреного контракту у файл для подальшої верифікації в CI
	contractPath := "order_contract.json"
	if err := builder.Export(contractPath); err != nil {
		t.Fatalf("помилка експорту контракту: %v", err)
	}
	t.Logf("Контракт успішно збережено у файл: %s", contractPath)
}
