func BookingWorkflow(ctx workflow.Context) (err error) {
    var compensations []func(workflow.Context)

    // Гарантоване виконання компенсацій у разі виникнення помилки
    defer func() {
        if err != nil {
            // Створюємо ізольований контекст, який ігнорує скасування батька
            disconnectedCtx, _ := workflow.NewDisconnectedContext(ctx)
            for i := len(compensations) - 1; i >= 0; i-- {
                compensations[i](disconnectedCtx)
            }
        }
    }()

    // Крок 1: Бронювання готелю
    err = workflow.ExecuteActivity(ctx, BookHotelActivity).Get(ctx, nil)
    if err != nil {
        return err
    }
    compensations = append(compensations, func(c workflow.Context) {
        workflow.ExecuteActivity(c, CancelHotelActivity)
    })

    // Крок 2: Оренда автомобіля
    err = workflow.ExecuteActivity(ctx, RentCarActivity).Get(ctx, nil)
    if err != nil {
        return err // Автоматично викличе CancelHotelActivity через defer
    }
    compensations = append(compensations, func(c workflow.Context) {
        workflow.ExecuteActivity(c, CancelCarActivity)
    })

    // Крок 3: Викуп авіаквитків
    err = workflow.ExecuteActivity(ctx, BookFlightActivity).Get(ctx, nil)
    if err != nil {
        return err // Викличе CancelCarActivity, а потім CancelHotelActivity
    }

    return nil
}
