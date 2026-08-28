typedef bool (*StopPredicateFunc)(
    const StepMetrics *metrics,
    void *user_data
);

EnumeratorStatus enumerator_run_until(
    EnumeratorHandle *handle,
    StopPredicateFunc stop_pred,
    void *user_data
);
