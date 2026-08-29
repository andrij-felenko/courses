// task_profiler.hpp — ядро профілювальника: калібрування, вимір, джитер, звіт.
//
// Помилки віддаються std::expected, а не кодом -1: викликач не має шансу
// проґавити «ідентифікатор поза межами» чи «DWT недоступний». Вимірювана
// область позначається RAII-об'єктом Scope — вихід із неї будь-яким шляхом
// закриває вимір.
#pragma once

#include "critical_section.hpp"
#include "dwt.hpp"
#include "task_stats.hpp"

#include <array>
#include <cstddef>
#include <expected>
#include <format>
#include <string_view>

namespace rt {

template <std::size_t MaxTasks = 8>
class TaskProfiler {
public:
    constexpr explicit TaskProfiler(std::uint32_t cpu_freq_hz) noexcept : clock_{cpu_freq_hz} {}

    TaskProfiler(const TaskProfiler&) = delete;
    TaskProfiler& operator=(const TaskProfiler&) = delete;

    // Вмикає DWT, чистить статистику й калібрує власний оверхед.
    [[nodiscard]] std::expected<void, ProfilerError> start() noexcept
    {
        if (clock_.hz() == 0U) {
            return std::unexpected(ProfilerError::BadFrequency);
        }
        if (!dwt::enable_cycle_counter()) {
            return std::unexpected(ProfilerError::HardwareMissing);
        }
        dwt::enable_event_counters();
        events_.reset();
        entries_ = {};
        overhead_cyc_ = calibrate();
        started_ = true;
        return {};
    }

    // period == 0 — точка спорадична, джитер для неї не рахується.
    [[nodiscard]] std::expected<void, ProfilerError>
    register_task(std::uint8_t id, std::string_view name, std::chrono::microseconds period) noexcept
    {
        if (id >= MaxTasks) {
            return std::unexpected(ProfilerError::InvalidId);
        }
        const cortex::CriticalSection guard;
        entries_[id] = Entry{};
        entries_[id].stats.name = name;
        entries_[id].stats.expected_period_cyc = clock_.from(period);
        return {};
    }

    void enter(std::uint8_t id) noexcept
    {
        const std::uint32_t now = dwt::cyccnt(); // мітку знімаємо першою дією
        if (!started_ || id >= MaxTasks) {
            return;
        }
        const cortex::CriticalSection guard;
        mark_enter(entries_[id], now);
    }

    void exit(std::uint8_t id) noexcept
    {
        const std::uint32_t stop = dwt::cyccnt();
        if (!started_ || id >= MaxTasks) {
            return;
        }
        const cortex::CriticalSection guard;
        mark_exit(entries_[id], stop);
    }

    [[nodiscard]] std::expected<TaskStats, ProfilerError> stats(std::uint8_t id) const noexcept
    {
        if (id >= MaxTasks) {
            return std::unexpected(ProfilerError::InvalidId);
        }
        if (!started_) {
            return std::unexpected(ProfilerError::NotStarted);
        }
        const cortex::CriticalSection guard; // 64-розрядне total_cyc — двома словами
        return entries_[id].stats;
    }

    [[nodiscard]] std::uint32_t overhead_cyc() const noexcept { return overhead_cyc_; }
    [[nodiscard]] const CycleClock& clock() const noexcept { return clock_; }

    // RAII на область видимості: profiler.scope(id) вимірює до кінця блоку,
    // хоч би скільки в ньому було виходів.
    class Scope {
    public:
        Scope(TaskProfiler& profiler, std::uint8_t id) noexcept : profiler_{profiler}, id_{id}
        {
            profiler_.enter(id_);
        }
        ~Scope() noexcept { profiler_.exit(id_); }

        Scope(const Scope&) = delete;
        Scope& operator=(const Scope&) = delete;

    private:
        TaskProfiler& profiler_;
        std::uint8_t id_;
    };

    [[nodiscard]] Scope scope(std::uint8_t id) noexcept { return Scope{*this, id}; }

    // Sink — будь-що викличне від std::string_view: UART, ITM, кільцевий буфер.
    template <class Sink>
    void report(Sink&& out) const
    {
        std::array<char, 160> line{};

        if (!started_) {
            out(std::string_view{"\r\nprofiler: CYCCNT недоступний, звіту немає\r\n"});
            return;
        }

        out(emit(line, "\r\n== ПРОФІЛЬ ВИКОНАННЯ ==  f={} Гц  оверхед={} такт.\r\n",
                 clock_.hz(), overhead_cyc_));
        out(std::string_view{
            " id  назва           викл.      min      avg      max   джитер      ISR\r\n"});
        out(std::string_view{
            " --  --------------  -------  -------  -------  -------  -------  -------  (мкс)\r\n"});

        for (std::size_t i = 0; i < MaxTasks; ++i) {
            const auto snapshot = stats(static_cast<std::uint8_t>(i));
            if (!snapshot || snapshot->call_count == 0U) {
                continue;
            }
            const TaskStats& s = *snapshot;
            out(emit(line, "{:>3}  {:<14}  {:>7}  {:>7}  {:>7}  {:>7}  {:>7}  {:>7}\r\n", i, s.name,
                     s.call_count, clock_.to_us(s.min_cyc).count(), clock_.to_us(s.avg_cyc()).count(),
                     clock_.to_us(s.max_cyc).count(), clock_.to_us(s.max_jitter_cyc).count(),
                     clock_.to_us(s.exc_cyc).count()));
            if (s.orphan_count != 0U || s.sleep_cyc != 0U) {
                out(emit(line, "      неспарених: {}, у сні: {} такт.\r\n", s.orphan_count,
                         s.sleep_cyc));
            }
        }
    }

private:
    // Публічний знімок плюс службові поля, яким у звіті немає чого робити.
    struct Entry {
        TaskStats stats{};
        std::uint32_t mark_exc_cyc{0};
        std::uint32_t mark_sleep_cyc{0};
        bool active{false};
        bool has_prev_enter{false};
    };

    void mark_enter(Entry& e, std::uint32_t now) noexcept
    {
        if (e.active) {
            e.stats.orphan_count++; // другий вхід без виходу: зріз загублено
        }
        if (e.has_prev_enter && e.stats.expected_period_cyc != 0U) {
            // беззнакова різниця лишається точною і через переповнення CYCCNT
            const std::uint32_t actual = now - e.stats.last_start_cyc;
            const std::uint32_t expected = e.stats.expected_period_cyc;
            const std::uint32_t jitter = actual > expected ? actual - expected : expected - actual;
            if (jitter > e.stats.max_jitter_cyc) {
                e.stats.max_jitter_cyc = jitter;
            }
        }
        events_.sample();
        e.mark_exc_cyc = events_.totals().exc;
        e.mark_sleep_cyc = events_.totals().sleep;
        e.stats.last_start_cyc = now;
        e.has_prev_enter = true;
        e.active = true;
    }

    void mark_exit(Entry& e, std::uint32_t stop) noexcept
    {
        if (!e.active) {
            // вихід без входу: перше перемикання контексту після старту
            // планувальника саме таке
            e.stats.orphan_count++;
            return;
        }

        std::uint32_t elapsed = stop - e.stats.last_start_cyc;
        elapsed = elapsed > overhead_cyc_ ? elapsed - overhead_cyc_ : 0U;

        events_.sample();
        e.stats.exc_cyc += events_.totals().exc - e.mark_exc_cyc;
        e.stats.sleep_cyc += events_.totals().sleep - e.mark_sleep_cyc;

        e.stats.last_duration_cyc = elapsed;
        e.stats.total_cyc += elapsed;
        e.stats.call_count++;
        if (elapsed < e.stats.min_cyc) {
            e.stats.min_cyc = elapsed;
        }
        if (elapsed > e.stats.max_cyc) {
            e.stats.max_cyc = elapsed;
        }
        e.active = false;
    }

    // Женемо порожню пару enter/exit тим самим шляхом, що й у бою, і беремо
    // мінімум із 32 повторів: будь-яке переривання чи промах кеша тільки додає
    // тактів, тож найменший результат і є чистий оверхед інструменту.
    [[nodiscard]] std::uint32_t calibrate() noexcept
    {
        Entry probe{};
        probe.stats.name = "calib";
        overhead_cyc_ = 0U; // поки калібруємось, віднімати ще нема чого

        for (int i = 0; i < 32; ++i) {
            const std::uint32_t start = dwt::cyccnt();
            {
                const cortex::CriticalSection guard;
                mark_enter(probe, start);
            }
            const std::uint32_t stop = dwt::cyccnt();
            {
                const cortex::CriticalSection guard;
                mark_exit(probe, stop);
            }
        }
        return probe.stats.call_count == 0U ? 0U : probe.stats.min_cyc;
    }

    template <class... Args>
    [[nodiscard]] static std::string_view emit(std::array<char, 160>& buffer,
                                               std::format_string<Args...> fmt, Args&&... args)
    {
        const auto result = std::format_to_n(buffer.data(), buffer.size(), fmt,
                                             std::forward<Args>(args)...);
        const auto used = static_cast<std::size_t>(result.out - buffer.data());
        return std::string_view{buffer.data(), used};
    }

    CycleClock clock_;
    dwt::EventCounters events_{};
    std::array<Entry, MaxTasks> entries_{};
    std::uint32_t overhead_cyc_{0};
    bool started_{false};
};

} // namespace rt
