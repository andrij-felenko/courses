func OnboardingWorkflow(ctx workflow.Context, userID string) error {
    // Крок 1: Миттєва дія
    err := workflow.ExecuteActivity(ctx, ChargeFeeActivity, userID, 500).Get(ctx, nil)
    if err != nil {
        return err
    }

    // Крок 2: Очікування зовнішньої дії тривалістю 3 дні
    workflow.Sleep(ctx, 3 * 24 * time.Hour)

    // Крок 3: Наступна дія після триденного сну
    return workflow.ExecuteActivity(ctx, SendWelcomeEmailActivity, userID).Get(ctx, nil)
}
