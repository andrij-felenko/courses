/* Отримання ресурсу з пулу з перевіркою дедлайну */
bool acquire_connection(std::mutex& pool_mtx,
                        std::condition_variable& pool_cv,
                        int& available_slots,
                        const DeadlineContext& ctx) {
    std::unique_lock<std::mutex> lock(pool_mtx);

    const auto predicate = [&] { return available_slots > 0; };
    while (!predicate()) {
        const auto remain = ctx.remaining();
        if (remain <= std::chrono::milliseconds::zero()) {
            return false; /* Дедлайн вичерпано під час очікування в пулі */
        }

        if (pool_cv.wait_for(lock, remain) == std::cv_status::timeout) {
            return false;
        }
    }

    --available_slots;
    return true;
}
