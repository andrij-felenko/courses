leaderelection.RunOrDie(ctx, leaderelection.LeaderElectionConfig{
    Lock:          leaseLock,
    LeaseDuration: 15 * time.Second,
    RenewDeadline: 10 * time.Second,
    RetryPeriod:   2 * time.Second,
    Callbacks: leaderelection.LeaderCallbacks{
        OnStartedLeading: func(ctx context.Context) {
            // Запуск монопольних горутин (білінг, шедулер)
            runBillingWorker(ctx)
        },
        OnStoppedLeading: func() {
            // Аварійне скасування: процес втратив лідерство
            log.Fatalf("Втрачено лідерство! Зупинка процесу.")
        },
        OnNewLeader: func(identity string) {
            log.Printf("Обрано нового лідера: %s", identity)
        },
    },
})
