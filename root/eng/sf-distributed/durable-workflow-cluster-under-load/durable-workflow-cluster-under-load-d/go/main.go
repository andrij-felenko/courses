func BillingAccountWorkflow(ctx workflow.Context, state AccountState) error {
    eventCount := 0

    for {
        // Очікування зовнішнього сигналу або таймера
        var signal DepositSignal
        selector := workflow.NewSelector(ctx)
        selector.AddReceive(workflow.GetSignalChannel(ctx, "Deposit"), func(c workflow.ReceiveChannel, _ bool) {
            c.Receive(ctx, &signal)
            state.Balance += signal.Amount
            eventCount++
        })
        selector.Select(ctx)

        // Перевірка порогу відсікання історії
        if eventCount >= 1000 || workflow.GetInfo(ctx).GetCurrentHistoryLength() >= 2000 {
            // Атомарний перехід: поточний RunID закривається, новий RunID стартує зі state
            return workflow.NewContinueAsNewError(ctx, BillingAccountWorkflow, state)
        }
    }
}
