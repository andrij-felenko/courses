func GenerateQuarterlyReportWorkflow(ctx workflow.Context, branchIDs []string) (Report, error) {
    // Створюємо слайс ф'ючерсів
    futures := make([]workflow.Future, len(branchIDs))

    // Запускаємо 100 активностей паралельно
    for i, id := range branchIDs {
        futures[i] = workflow.ExecuteActivity(ctx, FetchBranchDataActivity, id)
    }

    // Очікуємо завершення всіх задач (Fan-In / Join)
    results := make([]BranchData, len(branchIDs))
    for i, f := range futures {
        err := f.Get(ctx, &results[i])
        if err != nil {
            return Report{}, err
        }
    }

    return aggregateReport(results), nil
}
