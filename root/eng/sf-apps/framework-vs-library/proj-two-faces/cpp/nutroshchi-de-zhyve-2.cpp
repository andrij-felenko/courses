void Core::step(Clock::time_point now, std::span<const int> ready) noexcept
{
    // 1. дескриптори, які викликач побачив готовими
    for (int fd : ready) {
        const auto f = by_fd_.find(fd);
        if (f == by_fd_.end()) continue;          // не наш дескриптор — мовчки повз
        const Id id = f->second;
        Req& r = reqs_.at(id);

        char buf[1500];
        const ssize_t n = ::recv(r.fd, buf, sizeof buf, 0);
        if (n < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) continue;
            finish(id, r, Status::failed, errno, {});   // сюди приходить ECONNREFUSED
            continue;
        }
        const auto rtt =
            std::chrono::duration_cast<std::chrono::milliseconds>(now - r.sent_at);
        finish(id, r, Status::replied, 0, rtt);
    }

    // 2. те, чий строк уже настав
    while (!timers_.empty() && timers_.begin()->first <= now) {
        const Id id = timers_.begin()->second;
        Req& r = reqs_.at(id);
        timers_.erase(timers_.begin());
        r.timer = timers_.end();

        if (r.left > 0) send_probe(id, r, now);            // ще одна спроба
        else            finish(id, r, Status::timed_out, 0, {});
    }
}

void Core::finish(Id id, Req& r, Status st, int err,
                  std::chrono::milliseconds rtt) noexcept
{
    events_.push_back(Event{id, st, rtt, err, r.tag});  // спершу дочитати все з r
    if (r.timer != timers_.end()) timers_.erase(r.timer);
    by_fd_.erase(r.fd);
    ::close(r.fd);
    touch_watches();
    reqs_.erase(id);            // ↓ нижче цього рядка посилання r мертве
}

std::optional<Clock::time_point> Core::next_deadline() const noexcept
{
    if (timers_.empty()) return std::nullopt;   // строку немає взагалі
    return timers_.begin()->first;
}
