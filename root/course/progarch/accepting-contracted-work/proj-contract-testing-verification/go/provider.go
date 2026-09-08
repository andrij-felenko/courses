package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
)

// ProviderServer — реалізація HTTP-сервісу підрядника на базі net/http.
// Містить пам'яттєве сховище замовлень, підтримку налаштування станів для контрактних тестів
// та прапорець breakingChange для емуляції несумісних дефектів.
type ProviderServer struct {
	mu             sync.RWMutex
	orders         map[string]Order
	mux            *http.ServeMux
	breakingChange bool
}

// NewProviderServer ініціалізує сумісний сервіс підрядника, що відповідає контракту.
func NewProviderServer() *ProviderServer {
	p := &ProviderServer{
		orders:         make(map[string]Order),
		mux:            http.NewServeMux(),
		breakingChange: false,
	}
	p.routes()
	return p
}

// NewBrokenProviderServer ініціалізує дефектну версію сервісу підрядника
// із порушенням схеми відповідей та HTTP-статусів для демонстрації спрацювання CI-гейта.
func NewBrokenProviderServer() *ProviderServer {
	p := &ProviderServer{
		orders:         make(map[string]Order),
		mux:            http.NewServeMux(),
		breakingChange: true,
	}
	p.routes()
	return p
}

// routes конфігурує маршрути HTTP-сервера.
func (p *ProviderServer) routes() {
	p.mux.HandleFunc("/orders", p.handleOrders)
	p.mux.HandleFunc("/orders/", p.handleOrderByID)
}

// ServeHTTP реалізує стандартний інтерфейс http.Handler.
func (p *ProviderServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	p.mux.ServeHTTP(w, r)
}

// SetBreakingChange перемикає поведінку сервера між коректною та дефектною.
func (p *ProviderServer) SetBreakingChange(broken bool) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.breakingChange = broken
}

// SetupState встановлює необхідний передумовний стан сховища (Provider State).
func (p *ProviderServer) SetupState(state string) error {
	p.mu.Lock()
	defer p.mu.Unlock()

	switch state {
	case "сховище замовлень готове до запису":
		p.orders = make(map[string]Order)
		return nil

	case "замовлення ord-101 існує в системі підрядника", "замовлення ord-101 існує в системі":
		p.orders["ord-101"] = Order{
			ID:           "ord-101",
			CustomerName: "ТОВ Рога і Копита",
			Amount:       1500.50,
			Currency:     "UAH",
			Status:       "PENDING",
		}
		return nil

	default:
		return fmt.Errorf("невідомий стан провайдера: %q", state)
	}
}

// handleOrders обробляє створення нових замовлень (POST /orders).
func (p *ProviderServer) handleOrders(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "метод не підтримується", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "не вдалося прочитати тіло запиту", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	var req CreateOrderRequest
	if err := json.Unmarshal(body, &req); err != nil {
		http.Error(w, "некоректний JSON запиту", http.StatusBadRequest)
		return
	}

	if strings.TrimSpace(req.CustomerName) == "" || req.Amount <= 0 {
		http.Error(w, "некоректні параметри замовлення", http.StatusBadRequest)
		return
	}

	order := Order{
		ID:           "ord-101",
		CustomerName: req.CustomerName,
		Amount:       req.Amount,
		Currency:     req.Currency,
		Status:       "PENDING",
	}

	p.mu.Lock()
	p.orders[order.ID] = order
	isBroken := p.breakingChange
	p.mu.Unlock()

	w.Header().Set("Content-Type", "application/json")

	// Якщо увімкнено дефектний режим:
	// підрядник самовільно змінив статус з 201 на 200 та перейменував поле "amount" на "total_sum"
	if isBroken {
		w.WriteHeader(http.StatusOK)
		brokenResponse := map[string]any{
			"id":            order.ID,
			"customer_name": order.CustomerName,
			"total_sum":     order.Amount, // Порушення контракту: зміна назви поля
			"currency":      order.Currency,
			"status":        order.Status,
		}
		_ = json.NewEncoder(w).Encode(brokenResponse)
		return
	}

	// Сумісна коректна відповідь згідно з контрактом
	w.WriteHeader(http.StatusCreated)
	_ = json.NewEncoder(w).Encode(order)
}

// handleOrderByID обробляє запити на отримання замовлення за ID (GET /orders/{id}).
func (p *ProviderServer) handleOrderByID(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "метод не підтримується", http.StatusMethodNotAllowed)
		return
	}

	id := strings.TrimPrefix(r.URL.Path, "/orders/")
	if id == "" {
		http.Error(w, "ідентифікатор замовлення обов'язковий", http.StatusBadRequest)
		return
	}

	p.mu.RLock()
	order, exists := p.orders[id]
	isBroken := p.breakingChange
	p.mu.RUnlock()

	if !exists {
		http.Error(w, fmt.Sprintf("замовлення %s не знайдено", id), http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	// Якщо увімкнено дефектний режим:
	// підрядник випадково опустив обов'язкове поле "status" у відповіді
	if isBroken {
		brokenResponse := map[string]any{
			"id":            order.ID,
			"customer_name": order.CustomerName,
			"amount":        order.Amount,
			"currency":      order.Currency,
			// "status" відсутній — порушення очікувань клієнта
		}
		_ = json.NewEncoder(w).Encode(brokenResponse)
		return
	}

	_ = json.NewEncoder(w).Encode(order)
}
