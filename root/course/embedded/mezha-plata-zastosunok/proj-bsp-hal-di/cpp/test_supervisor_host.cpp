// test_supervisor_host.cpp — модульні тести супервізора на хості.
//
// Мок веде віртуальний годинник і журнал викликів, тож перевіряються
// не лише прапорці, а й порядок дій та витримки між ними.
#include "supervisor.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <optional>
#include <string_view>
#include <vector>

namespace {

int g_failures = 0;

void check(bool ok, std::string_view what)
{
    if (!ok) {
        ++g_failures;
        std::cerr << "[FAIL] " << what << '\n';
    }
}

enum class EvKind { Led, Power, Env, Sleep };

struct Event {
    EvKind kind{};
    int a{};   // LedId / PowerDomain / SleepMode; для Env — 1 успіх, 0 збій
    int b{};   // LedState / enable; для Sleep — тайм-аут у мс
    std::chrono::milliseconds at{};
};

class MockBoard final : public bsp::IBoardSupport {
public:
    // Керування сценарієм
    std::uint16_t voltage_mv{3800};
    bool battery_fault{false};
    unsigned env_fail_every{0};   // 0 — не збоїти; 3 — кожен третій виклик
    bool env_fail_always{false};

    // Спостережуваний стан
    bool sensors_powered{false};
    bool radio_powered{false};
    bsp::LedState warn_led{bsp::LedState::Off};
    bsp::LedState status_led{bsp::LedState::Off};
    std::vector<Event> events;

    bsp::Status led_set(bsp::LedId led, bsp::LedState state) noexcept override
    {
        (led == bsp::LedId::Warning ? warn_led : status_led) = state;
        push(EvKind::Led, static_cast<int>(led), static_cast<int>(state));
        return bsp::Status::Ok;
    }

    bsp::Status power_domain_set(bsp::PowerDomain domain, bool enable) noexcept override
    {
        (domain == bsp::PowerDomain::Sensors ? sensors_powered : radio_powered) = enable;
        push(EvKind::Power, static_cast<int>(domain), enable ? 1 : 0);
        return bsp::Status::Ok;
    }

    std::expected<bsp::BatteryMetrics, bsp::Status> get_battery_metrics() noexcept override
    {
        if (battery_fault) {
            return std::unexpected(bsp::Status::Timeout);
        }
        return bsp::BatteryMetrics{voltage_mv, 50};
    }

    std::expected<bsp::EnvironmentMetrics, bsp::Status> read_environment() noexcept override
    {
        ++env_calls_;
        bool fail = env_fail_always || !sensors_powered;
        if (!fail && env_fail_every != 0 && env_calls_ % env_fail_every == 0) {
            fail = true;
        }
        push(EvKind::Env, fail ? 0 : 1, 0);
        if (fail) {
            return std::unexpected(bsp::Status::BusFault);
        }
        return bsp::EnvironmentMetrics{2250, now_};
    }

    bsp::Status enter_low_power(bsp::SleepMode mode,
                                std::chrono::milliseconds timeout) noexcept override
    {
        push(EvKind::Sleep, static_cast<int>(mode), static_cast<int>(timeout.count()));
        now_ += timeout;   // сон рухає віртуальний годинник
        return bsp::Status::Ok;
    }

    void delay(std::chrono::milliseconds duration) noexcept override { now_ += duration; }

    [[nodiscard]] std::chrono::milliseconds uptime() const noexcept override { return now_; }

    // Пошук події від позиції from; a або b зі значенням -1 — «будь-яке».
    [[nodiscard]] std::optional<std::size_t> find(EvKind kind, int a = -1, int b = -1,
                                                  std::size_t from = 0) const
    {
        for (std::size_t i = from; i < events.size(); ++i) {
            const Event& e = events[i];
            if (e.kind != kind) continue;
            if (a >= 0 && e.a != a) continue;
            if (b >= 0 && e.b != b) continue;
            return i;
        }
        return std::nullopt;
    }

private:
    void push(EvKind kind, int a, int b) { events.push_back(Event{kind, a, b, now_}); }

    std::chrono::milliseconds now_{1000};
    unsigned env_calls_{0};
};

void test_normal_voltage()
{
    MockBoard board;
    board.voltage_mv = 3800;
    app::SystemSupervisor sup(board);

    sup.run_cycle();

    check(!sup.is_low_power_warning(), "3800 мВ: тривоги бути не має");
    check(!sup.is_critical_shutdown(), "3800 мВ: аварії бути не має");
    check(sup.has_fresh_env(), "3800 мВ: дані давачів отримано");
    check(sup.last_env() && sup.last_env()->temperature_centi_c == 2250,
          "3800 мВ: температура збережена");
    check(board.radio_powered, "3800 мВ: радіо дозволене");
    check(!board.sensors_powered, "3800 мВ: давачі знеструмлені вартовим");
    check(board.warn_led == bsp::LedState::Off, "3800 мВ: індикатор тривоги згашений");
    check(!board.find(EvKind::Sleep), "3800 мВ: сну не було");
    std::cout << "[OK] штатний цикл при 3800 мВ\n";
}

void test_warning_voltage()
{
    MockBoard board;
    board.voltage_mv = 3200;
    app::SystemSupervisor sup(board);

    sup.run_cycle();

    check(sup.is_low_power_warning(), "3200 мВ: тривога піднята");
    check(board.warn_led == bsp::LedState::On, "3200 мВ: індикатор тривоги горить");
    check(!board.radio_powered, "3200 мВ: радіо заблоковане");
    check(sup.has_fresh_env(), "3200 мВ: вимірювання ще виконується");
    check(!board.find(EvKind::Sleep), "3200 мВ: аварійного сну немає");
    std::cout << "[OK] попереджувальний поріг 3200 мВ\n";
}

void test_critical_shutdown()
{
    MockBoard board;
    board.voltage_mv = 2900;
    app::SystemSupervisor sup(board);

    sup.run_cycle();

    check(sup.is_critical_shutdown(), "2900 мВ: аварійне вимкнення");
    check(!board.sensors_powered, "2900 мВ: давачі знеструмлені");
    check(!board.radio_powered, "2900 мВ: радіо знеструмлене");

    const auto sleep_idx = board.find(EvKind::Sleep, static_cast<int>(bsp::SleepMode::Deep));
    check(sleep_idx.has_value(), "2900 мВ: увійшли в глибокий сон");
    if (sleep_idx) {
        check(board.events[*sleep_idx].b == app::kDeepSleep.count(),
              "2900 мВ: сон рівно на годину");
        const auto off_idx = board.find(EvKind::Power,
                                        static_cast<int>(bsp::PowerDomain::Sensors), 0);
        check(off_idx && *off_idx < *sleep_idx, "2900 мВ: живлення знято ДО сну");
    }
    std::cout << "[OK] критичний поріг 2900 мВ\n";
}

void test_settle_time_invariant()
{
    MockBoard board;
    app::SystemSupervisor sup(board);

    sup.run_cycle();

    const auto on_idx = board.find(EvKind::Power,
                                   static_cast<int>(bsp::PowerDomain::Sensors), 1);
    check(on_idx.has_value(), "інваріант: давачі вмикалися");
    if (!on_idx) return;

    const auto env_idx = board.find(EvKind::Env, -1, -1, *on_idx);
    check(env_idx.has_value(), "інваріант: читання давачів відбулося");
    if (!env_idx) return;

    const auto settle = board.events[*env_idx].at - board.events[*on_idx].at;
    check(settle >= app::kSensorSettle, "інваріант: витримка стабілізації >= 15 мс");
    std::cout << "[OK] витримка стабілізації " << settle.count() << " мс\n";
}

void test_fault_injection_recovers()
{
    MockBoard board;
    board.env_fail_every = 3;   // кожен третій виклик — збій шини
    app::SystemSupervisor sup(board);

    for (int i = 0; i < 5; ++i) {
        sup.run_cycle();
        check(sup.has_fresh_env(), "збої: повтор витягнув дані");
        check(!board.sensors_powered, "збої: живлення знято попри збій");
    }
    check(sup.env_fault_count() > 0, "збої: невдалі спроби пораховано");
    std::cout << "[OK] збій на кожен третій виклик, " << sup.env_fault_count()
              << " повторів\n";
}

void test_fault_injection_gives_up()
{
    MockBoard board;
    board.env_fail_always = true;   // давач мертвий
    app::SystemSupervisor sup(board);

    sup.run_cycle();   // якби був нескінченний цикл — тест би тут і повис

    check(!sup.has_fresh_env(), "мертвий давач: свіжих даних немає");
    check(sup.env_fault_count() == app::kEnvAttempts, "мертвий давач: рівно три спроби");
    check(!board.sensors_powered, "мертвий давач: вартовий зняв живлення");
    check(board.status_led == bsp::LedState::Off, "мертвий давач: індикатор згашено");
    std::cout << "[OK] мертвий давач: вихід без зависання\n";
}

void test_battery_read_fault()
{
    MockBoard board;
    board.battery_fault = true;
    app::SystemSupervisor sup(board);

    sup.run_cycle();

    check(sup.battery_fault_count() == 1, "збій АЦП: пораховано");
    check(board.warn_led == bsp::LedState::On, "збій АЦП: індикатор тривоги");
    check(!board.find(EvKind::Sleep), "збій АЦП: наосліп не засинаємо");
    check(!board.find(EvKind::Env), "збій АЦП: давачі не чіпаємо");
    std::cout << "[OK] збій читання батареї\n";
}

} // namespace

int main()
{
    test_normal_voltage();
    test_warning_voltage();
    test_critical_shutdown();
    test_settle_time_invariant();
    test_fault_injection_recovers();
    test_fault_injection_gives_up();
    test_battery_read_fault();

    if (g_failures != 0) {
        std::cerr << "\nПровалених перевірок: " << g_failures << '\n';
        return 1;
    }
    std::cout << "\nУсі тести пройдено на хості — без жодного мікроконтролера.\n";
    return 0;
}
