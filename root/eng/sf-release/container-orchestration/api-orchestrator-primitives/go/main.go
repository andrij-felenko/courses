// Request містить лише ключ ідентифікації об'єкта
type Request struct {
    types.NamespacedName
}

// Result керує наступною дією планувальника черги
type Result struct {
    // Requeue вказує негайно повернути ключ у чергу
    Requeue bool
    // RequeueAfter вказує поставити ключ у чергу з фіксованою затримкою
    RequeueAfter time.Duration
}

// Reconciler — фундаментальний інтерфейс обробника узгодження
type Reconciler interface {
    // Reconcile виконує читання стану, розрахунок різниці та коригувальні дії
    Reconcile(ctx context.Context, req Request) (Result, error)
}
