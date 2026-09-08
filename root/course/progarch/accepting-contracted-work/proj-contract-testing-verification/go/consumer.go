package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

var (
	// ErrOrderNotFound повертається, коли замовлення за вказаним ідентифікатором відсутнє.
	ErrOrderNotFound = errors.New("замовлення не знайдено")
	// ErrInvalidOrderData сигналізує про некоректні вхідні параметри замовлення.
	ErrInvalidOrderData = errors.New("некоректні вхідні дані замовлення")
	// ErrProviderFailure повідомляє про непередбачену помилку на стороні сервера підрядника.
	ErrProviderFailure = errors.New("збій у роботі сервісу підрядника")
)

// Order — доменна сутність замовлення, що очікується споживачем.
type Order struct {
	ID           string  `json:"id"`
	CustomerName string  `json:"customer_name"`
	Amount       float64 `json:"amount"`
	Currency     string  `json:"currency"`
	Status       string  `json:"status"`
}

// CreateOrderRequest — структура запиту на створення нового замовлення.
type CreateOrderRequest struct {
	CustomerName string  `json:"customer_name"`
	Amount       float64 `json:"amount"`
	Currency     string  `json:"currency"`
}

// ConsumerClient — типізований HTTP-клієнт замовника для взаємодії з API підрядника.
type ConsumerClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewConsumerClient створює новий клієнт замовника з налаштованим базовим URL та таймаутом.
func NewConsumerClient(baseURL string, timeout time.Duration) *ConsumerClient {
	return &ConsumerClient{
		baseURL: strings.TrimRight(baseURL, "/"),
		httpClient: &http.Client{
			Timeout: timeout,
		},
	}
}

// CreateOrder надсилає POST-запит на створення нового замовлення та валідує результат.
func (c *ConsumerClient) CreateOrder(ctx context.Context, req CreateOrderRequest) (*Order, error) {
	if strings.TrimSpace(req.CustomerName) == "" {
		return nil, fmt.Errorf("%w: ім'я замовника обов'язкове", ErrInvalidOrderData)
	}
	if req.Amount <= 0 {
		return nil, fmt.Errorf("%w: сума замовлення має бути більшою за нуль", ErrInvalidOrderData)
	}

	payload, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("помилка кодування запиту в JSON: %w", err)
	}

	endpoint := fmt.Sprintf("%s/orders", c.baseURL)
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, bytes.NewReader(payload))
	if err != nil {
		return nil, fmt.Errorf("помилка формування HTTP-запиту: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("мережева помилка виконання запиту: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("не вдалося прочитати тіло відповіді: %w", err)
	}

	switch resp.StatusCode {
	case http.StatusCreated:
		var created Order
		if err := json.Unmarshal(bodyBytes, &created); err != nil {
			return nil, fmt.Errorf("помилка розбору відповіді провайдера: %w", err)
		}
		return &created, nil
	case http.StatusBadRequest:
		return nil, fmt.Errorf("%w: %s", ErrInvalidOrderData, string(bodyBytes))
	default:
		return nil, fmt.Errorf("%w (HTTP %d): %s", ErrProviderFailure, resp.StatusCode, string(bodyBytes))
	}
}

// GetOrder запитує деталі замовлення за його ідентифікатором.
func (c *ConsumerClient) GetOrder(ctx context.Context, id string) (*Order, error) {
	if strings.TrimSpace(id) == "" {
		return nil, fmt.Errorf("%w: ідентифікатор не може бути порожнім", ErrInvalidOrderData)
	}

	endpoint := fmt.Sprintf("%s/orders/%s", c.baseURL, url.PathEscape(id))
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("помилка формування HTTP-запиту: %w", err)
	}

	httpReq.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("мережева помилка під час отримання замовлення: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("не вдалося прочитати відповідь: %w", err)
	}

	switch resp.StatusCode {
	case http.StatusOK:
		var order Order
		if err := json.Unmarshal(bodyBytes, &order); err != nil {
			return nil, fmt.Errorf("помилка десеріалізації замовлення: %w", err)
		}
		return &order, nil
	case http.StatusNotFound:
		return nil, fmt.Errorf("%w: id=%s", ErrOrderNotFound, id)
	default:
		return nil, fmt.Errorf("%w (HTTP %d): %s", ErrProviderFailure, resp.StatusCode, string(bodyBytes))
	}
}
