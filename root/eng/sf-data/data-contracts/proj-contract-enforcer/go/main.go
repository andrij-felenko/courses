package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"time"
)

type OrderEvent struct {
	EventID          string `json:"event_id"`
	OrderID          string `json:"order_id"`
	UserID           string `json:"user_id"`
	OrderState       string `json:"order_state"`
	Currency         string `json:"currency"`
	TotalAmountCents int64  `json:"total_amount_cents"`
	TaxAmountCents   int64  `json:"tax_amount_cents"`
	ItemsCount       int32  `json:"items_count"`
	CreatedAt        string `json:"created_at"`
}

type DlqEnvelope struct {
	DlqID           string `json:"dlq_id"`
	FailedAt        string `json:"failed_at"`
	ContractVersion string `json:"contract_version"`
	ErrorReason     string `json:"error_reason"`
	RawPayload      string `json:"raw_payload"`
}

type DataContractValidator struct {
	version     string
	validStates map[string]bool
}

func NewValidator(version string) *DataContractValidator {
	return &DataContractValidator{
		version: version,
		validStates: map[string]bool{
			"PENDING": true, "PAID": true, "PROCESSING": true,
			"SHIPPED": true, "CANCELLED": true, "REFUNDED": true,
		},
	}
}

func (v *DataContractValidator) Validate(ev *OrderEvent) error {
	if ev.EventID == "" || ev.OrderID == "" || ev.UserID == "" {
		return errors.New("відсутній обов'язковий ідентифікатор")
	}
	if ev.TotalAmountCents < 0 {
		return errors.New("total_amount_cents не може бути від'ємним")
	}
	if ev.ItemsCount <= 0 || ev.ItemsCount > 500 {
		return errors.New("items_count має бути в діапазоні [1, 500]")
	}
	if !v.validStates[ev.OrderState] {
		return fmt.Errorf("недопустимий статус order_state: %s", ev.OrderState)
	}
	if len(ev.Currency) != 3 {
		return errors.New("код currency має складатись з 3 символів")
	}
	if ev.TaxAmountCents > ev.TotalAmountCents {
		return errors.New("tax_amount_cents перевищує total_amount_cents")
	}
	return nil
}

type IngestionGateway struct {
	validator *DataContractValidator
	DwhSink   []OrderEvent
	DlqSink   []DlqEnvelope
}

func (g *IngestionGateway) Process(rawJSON string) {
	var ev OrderEvent
	if err := json.Unmarshal([]byte(rawJSON), &ev); err != nil {
		g.routeToDlq(rawJSON, "Помилка парсингу JSON: "+err.Error())
		return
	}
	if err := g.validator.Validate(&ev); err != nil {
		g.routeToDlq(rawJSON, err.Error())
		return
	}
	g.DwhSink = append(g.DwhSink, ev)
}

func (g *IngestionGateway) routeToDlq(payload, reason string) {
	g.DlqSink = append(g.DlqSink, DlqEnvelope{
		DlqID:           "dlq-uuid-go-mock",
		FailedAt:        time.Now().UTC().Format(time.RFC3339),
		ContractVersion: g.validator.version,
		ErrorReason:     reason,
		RawPayload:      payload,
	})
}
