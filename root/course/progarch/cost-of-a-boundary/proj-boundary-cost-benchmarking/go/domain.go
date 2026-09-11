package boundarybench

import (
	"errors"
)

// ErrNilOrder повертається, коли передано nil замість структури замовлення.
var ErrNilOrder = errors.New("замовлення не може бути nil")

// OrderItem представляє окрему товарну позицію в замовленні.
type OrderItem struct {
	SKU      string `json:"sku"`
	Quantity int    `json:"quantity"`
	Price    int64  `json:"price"` // ціна в копійках/центах для точності розрахунків
}

// Order — доменна сутність замовлення, яка валідується на всіх типах меж.
type Order struct {
	ID         string      `json:"id"`
	CustomerID string      `json:"customer_id"`
	Items      []OrderItem `json:"items"`
	Total      int64       `json:"total"`
}

// ValidationResponse містить результат валідації та опис причини відхилення.
type ValidationResponse struct {
	Valid bool   `json:"valid"`
	Error string `json:"error,omitempty"`
}

// OrderValidator — уніфікований інтерфейсний контракт валідації для порівняння меж.
type OrderValidator interface {
	Validate(order *Order) (ValidationResponse, error)
}

// ValidateOrder виконує чисту бізнес-перевірку замовлення без накладних витрат швів.
func ValidateOrder(order *Order) (ValidationResponse, error) {
	if order == nil {
		return ValidationResponse{Valid: false, Error: "замовлення є nil"}, ErrNilOrder
	}
	if order.ID == "" {
		return ValidationResponse{Valid: false, Error: "порожній id замовлення"}, nil
	}
	if order.CustomerID == "" {
		return ValidationResponse{Valid: false, Error: "порожній customer_id"}, nil
	}
	if len(order.Items) == 0 {
		return ValidationResponse{Valid: false, Error: "список товарів порожній"}, nil
	}

	var sum int64
	for _, item := range order.Items {
		if item.Quantity <= 0 {
			return ValidationResponse{Valid: false, Error: "кількість товару повинна бути > 0"}, nil
		}
		if item.Price <= 0 {
			return ValidationResponse{Valid: false, Error: "ціна товару повинна бути > 0"}, nil
		}
		sum += int64(item.Quantity) * item.Price
	}

	if sum != order.Total {
		return ValidationResponse{Valid: false, Error: "сума позицій не відповідає загальній сумі замовлення"}, nil
	}

	return ValidationResponse{Valid: true}, nil
}

// NewSampleValidOrder створює еталонне коректне замовлення для бенчмарків.
func NewSampleValidOrder() *Order {
	return &Order{
		ID:         "ord-98421",
		CustomerID: "cust-55102",
		Items: []OrderItem{
			{SKU: "CPU-X86-64", Quantity: 2, Price: 15000},
			{SKU: "RAM-DDR5-32G", Quantity: 4, Price: 4000},
			{SKU: "SSD-NVME-2T", Quantity: 1, Price: 6000},
		},
		Total: 52000,
	}
}

// NewSampleInvalidOrder створює некоректне замовлення для тестування відхилення.
func NewSampleInvalidOrder() *Order {
	order := NewSampleValidOrder()
	order.Total = 99999 // штучна невідповідність суми позиціям
	return order
}
