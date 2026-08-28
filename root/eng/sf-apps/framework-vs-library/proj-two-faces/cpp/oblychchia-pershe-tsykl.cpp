// probe.hpp, поруч із Core: помічник потрібен обом обличчям.
inline int ms_until(Clock::time_point when, Clock::time_point now) noexcept
{
    if (when <= now) return 0;
    const auto ms =
        std::chrono::duration_cast<std::chrono::milliseconds>(when - now).count();
    // +1, бо duration_cast відкидає дробову частину: за 0.4 мс до строку
    // без нього вийшов би timeout = 0 і цикл почав би крутитися вхолосту.
    return static_cast<int>(std::min<long long>(ms + 1, 1000));
}

// ── твій головний цикл; ядро тут — звичайна бібліотека ──
std::vector<pollfd> pfds;
std::vector<int>    ready;
std::uint64_t       seen_gen  = ~0ull;
std::size_t         core_base = 0;

while (running) {
    if (core.watch_generation() != seen_gen) {   // набір ядра змінився
        pfds.clear();
        my_own_fds(pfds);                        // спершу СВОЇ дескриптори
        core_base = pfds.size();                 // далі — суцільним шматком ядрові
        for (const probe::Watch& w : core.watches()) {
            pollfd p{};
            p.fd     = w.fd;
            p.events = static_cast<short>((w.want_read  ? POLLIN  : 0) |
                                          (w.want_write ? POLLOUT : 0));
            pfds.push_back(p);
        }
        seen_gen = core.watch_generation();
    }

    const auto now  = probe::Clock::now();
    auto       wake = my_next_deadline();        // std::optional, твій власний строк
    if (auto d = core.next_deadline(); d && (!wake || *d < *wake)) wake = d;
    const int timeout = wake ? ms_until(*wake, now) : 1000;

    if (::poll(pfds.data(), static_cast<nfds_t>(pfds.size()), timeout) < 0) {
        if (errno == EINTR) continue;
        break;
    }

    ready.clear();
    for (std::size_t i = core_base; i < pfds.size(); ++i)
        if (pfds[i].revents) ready.push_back(pfds[i].fd);

    core.step(probe::Clock::now(), ready);              // увесь крок ядра
    while (auto ev = core.take_event()) on_result(*ev); // наслідки — поза кроком

    my_own_work(pfds);                                  // а тут — твої власні справи
}
