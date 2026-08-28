func DevicePollingWorkflow(ctx workflow.Context, deviceState State) error {
    for i := 0; i < 1000; i++ {
        // Опитування пристрою та оновлення стану
        deviceState = pollDevice(ctx, deviceState)
        workflow.Sleep(ctx, 10 * time.Second)
    }

    // Досягнуто ліміту ітерацій: перезапуск із чистою історією
    return workflow.NewContinueAsNewError(ctx, DevicePollingWorkflow, deviceState)
}
