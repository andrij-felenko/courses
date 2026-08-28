// probe.cpp
Id Core::add(Clock::time_point now, const sockaddr_in& to,
             std::string payload, void* tag)
{
    const Id id = ++last_id_;                       // id ніколи не повторюється
    int fd = ::socket(AF_INET, SOCK_DGRAM | SOCK_NONBLOCK, 0);  // Linux;
                        // на macOS — окремим fcntl(fd, F_SETFL, O_NONBLOCK)
    if (fd < 0 || ::connect(fd, reinterpret_cast<const sockaddr*>(&to), sizeof to) < 0) {
        if (fd >= 0) ::close(fd);
        events_.push_back(Event{id, Status::failed, {}, errno, tag});
        return id;                 // id виданий, і подія за ним уже лежить у черзі
    }
    auto [it, _] = reqs_.emplace(id, Req{fd, std::move(payload), tries_,
                                         tag, now, timers_.end()});
    by_fd_[fd] = id;
    touch_watches();
    send_probe(id, it->second, now);
    return id;
}

void Core::send_probe(Id id, Req& r, Clock::time_point now) noexcept
{
    const ssize_t n = ::send(r.fd, r.payload.data(), r.payload.size(), 0);
    if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
        finish(id, r, Status::failed, errno, {});
        return;
    }
    r.sent_at = now;                 // EAGAIN тут рахуємо за втрачений пакет:
    --r.left;                        // повторна спроба однаково прийде за строком
    r.timer = timers_.emplace(now + rto_, id);
}
