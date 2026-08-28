// go
package main

import (
	"errors"
	"fmt"
)

type OrderPayloadV1 struct {
	OrderID string  `json:"order_id"`
	Amount  float64 `json:"amount"`
}

func sendBillingRequestV1(payload OrderPayloadV1) error {
	fmt.Printf("[REST Client Go] Sending Order=%s, Amount=%.2f\n", payload.OrderID, payload.Amount)
	
	// Сервер v2 чекає tax_identifier
	serverRequiresTaxID := true
	if serverRequiresTaxID {
		return errors.New("HTTP 400 Bad Request: missing tax_identifier")
	}
	return nil
}

func main() {
	order := OrderPayloadV1{OrderID: "ORD-9901", Amount: 149.99}
	if err := sendBillingRequestV1(order); err != nil {
		fmt.Printf("[System Error] %v\n", err)
	}
}
