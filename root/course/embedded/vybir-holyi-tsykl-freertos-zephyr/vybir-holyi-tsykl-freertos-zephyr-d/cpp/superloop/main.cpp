// Голий супер-цикл на C++: замість трьох if-ів із таймштампами — таблиця
// робіт. Планувальника від цього не з'являється: усе так само один стек,
// одна черговість і жодного витіснення, просто перелік видно одним поглядом.
#include "bme280.hpp"
#include "board.hpp"
#include "ssd1306.hpp"

#include <algorithm>
#include <array>
#include <chrono>

using board::ms;

namespace {

board::I2cBus g_i2c{0x76};
app::Bme280 g_sensor{g_i2c};
app::Ssd1306 g_screen;

struct Stats {
    ms gap_max{0};
    ms gap_min{ms::max()};
    ms flush_max{0};
    std::uint32_t bus_errors{0};
};

Stats g_stats;
std::int32_t g_temperature{0};
bool g_have_sample{false};
bool g_screen_ready{false};
ms g_last_sensor{0};

void job_sensor(ms now)
{
    if (g_last_sensor.count() != 0) {
        const ms gap = now - g_last_sensor;
        g_stats.gap_max = std::max(g_stats.gap_max, gap);
        g_stats.gap_min = std::min(g_stats.gap_min, gap);
    }
    g_last_sensor = now;
    g_sensor.start(now);
}

void job_poll(ms now)
{
    auto result = g_sensor.poll(now);
    if (!result) {
        ++g_stats.bus_errors; // датчик сам піде на повторну ініціалізацію
        return;
    }
    if (result->has_value()) {
        g_temperature = (*result)->centi_celsius;
        g_have_sample = true;
    }
}

void job_screen(ms)
{
    if (!g_screen_ready) {
        g_screen_ready = g_screen.begin().has_value();
        if (!g_screen_ready) {
            return;
        }
    }

    g_screen.clear();
    if (g_have_sample) {
        g_screen.number(0, 0, g_temperature, 2);
        g_screen.bar(2, g_temperature, -1000, 5000);
    }
    g_screen.number(0, 4, static_cast<std::int32_t>(g_stats.gap_max.count()), 0);
    g_screen.number(40, 4, static_cast<std::int32_t>(g_stats.gap_min.count()), 0);
    g_screen.number(80, 4, static_cast<std::int32_t>(g_stats.flush_max.count()), 0);
    g_screen.number(0, 6, static_cast<std::int32_t>(g_sensor.errors() + g_stats.bus_errors), 0);

    // Ось та сама блокуюча ділянка. Міряємо її тим самим лічильником, яким
    // міряємо період датчика, — і на екрані видно, як одне псує інше.
    if (auto took = g_screen.flush()) {
        g_stats.flush_max = std::max(g_stats.flush_max, *took);
    } else {
        g_screen_ready = false;
    }
}

struct Job {
    ms period;
    ms next;
    void (*run)(ms);
};

std::array<Job, 3> g_jobs{{
    {ms{100}, ms{0}, &job_sensor},
    {ms{0}, ms{0}, &job_poll},   // період 0 — крок автомата на кожному оберті
    {ms{500}, ms{500}, &job_screen},
}};

} // namespace

extern "C" void SysTick_Handler()
{
    ++board::g_ticks;
}

int main()
{
    SystemCoreClockUpdate();
    board::start_systick(SystemCoreClock);
    board::I2cBus::configure();
    board::SpiBus::configure();

    g_screen_ready = g_screen.begin().has_value();
    if (!g_sensor.begin()) {
        // Датчик міг просто пізніше подати живлення: автомат сам повторить
        // спробу, а прилад тим часом лишається живим.
        g_stats.bus_errors = 1;
    }
    board::start_watchdog();

    for (;;) {
        const ms now = board::now();

        for (Job &job : g_jobs) {
            if (now >= job.next) {
                job.next = (job.period.count() == 0) ? now : now + job.period;
                job.run(now);
            }
        }

        board::kick_watchdog();
    }
}
