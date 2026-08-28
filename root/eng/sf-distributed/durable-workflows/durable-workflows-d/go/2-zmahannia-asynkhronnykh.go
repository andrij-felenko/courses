func FastQuoteWorkflow(ctx workflow.Context) (Quote, error) {
    selector := workflow.NewSelector(ctx)
    var winningQuote Quote

    for _, vendor := range []string{"VendorA", "VendorB", "VendorC"} {
        f := workflow.ExecuteActivity(ctx, RequestQuoteActivity, vendor)
        selector.AddFuture(f, func(f workflow.Future) {
            f.Get(ctx, &winningQuote)
        })
    }

    // Чекаємо першого переможця
    selector.Select(ctx)
    return winningQuote, nil
}
