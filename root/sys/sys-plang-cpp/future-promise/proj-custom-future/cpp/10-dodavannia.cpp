template <typename F>
auto then(F&& func) {
    using R = std::invoke_result_t<F, T>;
    custom_promise<R> next_promise;
    auto next_future = next_promise.get_future();

    std::unique_lock<std::mutex> lock(state_->mtx);
    if (state_->ready) {
        lock.unlock();
        // Якщо результат уже готовий, виконуємо продовження негайно
        try {
            next_promise.set_value(func(std::get<T>(state_->storage)));
        } catch (...) {
            next_promise.set_exception(std::current_exception());
        }
    } else {
        // Якщо результат ще не готовий, зберігаємо функцію в очікування
        state_->continuation = [st = state_, p = std::move(next_promise), f = std::forward<F>(func)]() mutable {
            try {
                p.set_value(f(std::get<T>(st->storage)));
            } catch (...) {
                p.set_exception(std::current_exception());
            }
        };
    }
    return next_future;
}
