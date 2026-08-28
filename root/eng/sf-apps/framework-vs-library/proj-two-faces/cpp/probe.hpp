// probe.hpp — ЯДРО. Жодного циклу, жодного sleep, жодного poll усередині.
#pragma once
#include <chrono>
#include <cstdint>
#include <optional>
#include <span>
#include <string>
#include <netinet/in.h>

namespace probe {

using Clock = std::chrono::steady_clock;
using Id    = std::uint64_t;

enum class Status { replied, timed_out, canceled, failed };

struct Event {
    Id                        id;
    Status                    status;
    std::chrono::milliseconds rtt{0};        // важить лише для replied
    int                       err  = 0;      // errno, важить лише для failed
    void*                     tag  = nullptr;// те, що дав викликач у add()
};

struct Watch { int fd; bool want_read; bool want_write; };

class Core {
public:
    Core(std::chrono::milliseconds rto, int tries);   // rto > 0
    ~Core();                                          // закриє всі свої дескриптори

    // Годинник ядро НЕ читає саме — час приходить аргументом.
    Id   add(Clock::time_point now, const sockaddr_in& to,
             std::string payload, void* tag = nullptr);
    void cancel(Id id) noexcept;        // подія canceled прийде однаково
    void cancel_all() noexcept;

    // ── чотири відповіді чужому циклові ──
    void step(Clock::time_point now, std::span<const int> ready) noexcept;
    std::optional<Clock::time_point> next_deadline() const noexcept;
    std::span<const Watch>           watches() const;      // може виділити пам'ять
    std::uint64_t watch_generation()  const noexcept;      // змінилось — перечитай watches()

    std::optional<Event> take_event() noexcept;
    std::size_t          active() const noexcept;
};

} // namespace probe
