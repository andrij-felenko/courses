using namespace std::chrono;

// Отримання найближчої точки часу закінчення таймауту з мінімальної купи
steady_clock::time_point next_expiry = timer_heap.top().expiry_time;
steady_clock::time_point now = steady_clock::now();

// Розрахунок інтервалу очікування
int timeout_ms = 0;
if (next_expiry > now) {
    // Безпечне перетворення тривалості у мілісекунди для epoll_wait
    auto dur = duration_cast<milliseconds>(next_expiry - now);
    timeout_ms = static_cast<int>(dur.count());
} else {
    // Таймаут вже минув: epoll_wait повинен повернути керування негайно (0 ms)
    timeout_ms = 0;
}

int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, timeout_ms);
