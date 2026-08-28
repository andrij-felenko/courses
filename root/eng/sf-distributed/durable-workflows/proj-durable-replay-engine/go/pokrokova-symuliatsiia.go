func main() {
	fmt.Println("=== СТАРТ РОБОЧОГО ПРОЦЕСУ ===")
	history := []WorkflowEvent{
		{Type: EventWorkflowStarted, Input: "user=Andrii"},
	}

	// Ітерація 1: Перший запуск
	ctx1 := NewWorkflowContext(history)
	_, err := OrderFulfillmentWorkflow(ctx1, "order-101")
	if errors.Is(err, ErrYield) {
		fmt.Println("[Вузол 1] Заплановано активність:", ctx1.newEvents[0].ActivityName)
		history = append(history, ctx1.newEvents...)
	}

	// Емуляція виконання активності
	fmt.Println("[Worker] Виконано ProcessPayment -> OK")
	history = append(history, WorkflowEvent{
		Type:         EventActivityCompleted,
		ActivityName: "ProcessPayment",
		Result:       "PAYMENT_OK_#9981",
	})

	// Аварія та Replay на Вузлі 2
	fmt.Println("\n!!! Аварія Вузла 1 -> Replay на Вузлі 2")
	ctx2 := NewWorkflowContext(history)
	_, err = OrderFulfillmentWorkflow(ctx2, "order-101")
	if errors.Is(err, ErrYield) {
		fmt.Println("[Вузол 2] Replay пройшов! Наступна активність:", ctx2.newEvents[0].ActivityName)
		history = append(history, ctx2.newEvents...)
	}
}
