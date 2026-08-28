    Shared<T> lock() const {
        if (!cb_) return {};
        long s = cb_->strong.load(std::memory_order_relaxed);
        while (s != 0) {                          // поки хтось іще володіє
            if (cb_->strong.compare_exchange_weak(
                    s, s + 1, std::memory_order_relaxed))
                return Shared<T>(cb_);            // підняли strong з s до s+1
            // невдача: s оновлено поточним значенням — пробуємо знову
        }
        return {};                                // strong досяг нуля — об'єкт мертвий
    }
