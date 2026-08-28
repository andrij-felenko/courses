// probe_run.hpp — ОБОЛОНКА. Нічого, крім циклу.
#pragma once
#include "probe.hpp"
#include <exception>
#include <poll.h>
#include <vector>

namespace probe {

template <class OnEvent>
void run(Core& core, OnEvent&& on_event)
{
    std::vector<pollfd> pfds;
    std::vector<int>    ready;
    std::uint64_t       seen_gen = ~0ull;
    std::exception_ptr  escaped;

    while (!escaped && core.active() > 0) {
        if (core.watch_generation() != seen_gen) {
            pfds.clear();
            for (const Watch& w : core.watches()) {
                pollfd p{};
                p.fd     = w.fd;
                p.events = static_cast<short>(POLLIN);
                pfds.push_back(p);
            }
            seen_gen = core.watch_generation();
        }

        const auto now = Clock::now();
        const auto d   = core.next_deadline();
        const int  timeout = d ? ms_until(*d, now) : 1000;

        if (::poll(pfds.data(), static_cast<nfds_t>(pfds.size()), timeout) < 0) {
            if (errno == EINTR) continue;
            break;
        }

        ready.clear();
        for (const pollfd& p : pfds)
            if (p.revents) ready.push_back(p.fd);

        core.step(Clock::now(), ready);

        while (auto ev = core.take_event()) {
            try { on_event(*ev); }
            catch (...) { escaped = std::current_exception(); break; }
        }
    }
    // Недоставлені події лишаються В ЯДРІ: хто зловить виняток, забере їх
    // тим самим take_event(). Оболонка не ковтає нічого й не тримає нічого.
    if (escaped) std::rethrow_exception(escaped);
}

} // namespace probe
