// Приклад виклику workflow.GetVersion у середовищі Go/Temporal
version := workflow.GetVersion(ctx, "ChangeID_AddFraudCheck", workflow.DefaultVersion, 1)
if version == workflow.DefaultVersion {
    // Стара поведінка для процесів, що стартували до релізу
    ctx.ExecuteActivity("ProcessPayment", orderID)
} else {
    // Нова логіка для всіх нових процесів
    ctx.ExecuteActivity("CheckFraudScore", orderID)
    ctx.ExecuteActivity("ProcessPayment", orderID)
}
