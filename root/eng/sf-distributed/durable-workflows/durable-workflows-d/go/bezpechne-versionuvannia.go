// Версія 2 (КОРЕКТНА МІГРАЦІЯ ЧЕРЕЗ GetVersion):
func OrderWorkflow(ctx workflow.Context) error {
    // Вказуємо унікальний ID зміни та діапазон версій
    v := workflow.GetVersion(ctx, "add-address-validation", workflow.DefaultVersion, 1)
    
    if v == 1 {
        // Нові процеси виконають валідацію
        workflow.ExecuteActivity(ctx, ValidateAddressActivity).Get(ctx, nil)
    }
    // Старі процеси з v == DefaultVersion пропустять цей блок і підуть далі

    workflow.ExecuteActivity(ctx, ReserveInventoryActivity).Get(ctx, nil)
    workflow.ExecuteActivity(ctx, ProcessPaymentActivity).Get(ctx, nil)
    return nil
}
