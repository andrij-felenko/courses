// Стенд для арбітра: модельний час, чотири станції в ефірі й сценарій, що
// проганяє всі переходи — захоплення токена, передачу зміни, втрату звʼязку
// й перехоплення командиром.
//
// На борту цю роль виконують три задачі FreeRTOS: приймач телеметрії кличе
// process_heartbeat(), задача ручного керування на 50 Гц — flight_allowed(),
// таймер — tick(). Тут вони згорнуті в один цикл, щоб час був відтворюваним.
#include <array>
#include <format>
#include <iostream>
#include <string_view>

#include "authority.hpp"

namespace {

using namespace gcs;
using namespace std::chrono_literals;

constexpr Millis kTick{20};        // період задачі-таймера
constexpr Millis kHeartbeatRate{100};  // станції озиваються 10 разів на секунду

constexpr std::uint8_t kAlpha  = 10;  // пілот-1
constexpr std::uint8_t kBravo  = 20;  // пілот-2, змінний
constexpr std::uint8_t kSensor = 30;  // оператор корисного навантаження
constexpr std::uint8_t kCmd    = 40;  // командир
constexpr std::uint8_t kGhost  = 99;  // станція, якої в ефірі немає

struct SimStation {
    std::uint8_t id;
    Roles        roles;
    bool         transmitting;  // чи чути її на борту просто зараз
};

class Bench {
public:
    explicit Bench(StationArbiter& arbiter) noexcept : arbiter_{arbiter} {}

    [[nodiscard]] Millis now() const noexcept { return now_; }

    void advance(Millis span)
    {
        for (Millis spent{0}; spent < span; spent += kTick) {
            now_ += kTick;
            hb_timer_ += kTick;
            if (hb_timer_ >= kHeartbeatRate) {
                hb_timer_ = Millis{0};
                for (const auto& station : net_) {
                    if (station.transmitting) {
                        (void)arbiter_.process_heartbeat(station.id, station.roles, now_);
                    }
                }
            }
            arbiter_.tick(now_);
        }
    }

    void set_transmitting(std::uint8_t id, bool on) noexcept
    {
        for (auto& station : net_) {
            if (station.id == id) {
                station.transmitting = on;
            }
        }
    }

    // Ширину під українську колонку не ставимо: std::format рахує байти, а не
    // літери, тож рівняти по ній нема сенсу.
    void say(std::string_view what, std::string_view result) const
    {
        std::cout << std::format("[{:6} мс] {} -> {} [{}, пілот={}]\n", now_.count(), what,
                                 result, to_string(arbiter_.state()), arbiter_.active_pilot());
    }

    void say(std::string_view what, Error error) const { say(what, to_string(error)); }
    void say(std::string_view what, bool allowed) const
    {
        say(what, allowed ? "ПРОПУЩЕНО" : "ВІДКИНУТО");
    }

    template <typename T>
    void say(std::string_view what, const std::expected<T, Error>& result) const
    {
        say(what, result ? std::string_view{"OK"} : to_string(result.error()));
    }

private:
    StationArbiter& arbiter_;
    Millis now_{0};
    Millis hb_timer_{0};
    std::array<SimStation, 4> net_{{
        {kAlpha,  Roles{Role::Pilot} | Role::Monitor,     true},
        {kBravo,  Roles{Role::Pilot} | Role::Monitor,     true},
        {kSensor, Roles{Role::Payload} | Role::Monitor,   true},
        {kCmd,    Roles{Role::Commander} | Role::Monitor, true},
    }};
};

}  // namespace

int main()
{
    StationArbiter arbiter{0x0BADF00DU, Millis{0}};
    Bench bench{arbiter};

    bench.advance(200ms);  // станції встигають назватися
    bench.say("борт піднявся, реєстр наповнено", std::string_view{"—"});

    // 1. Захоплення вільного токена.
    auto alpha_token = arbiter.request_pilot_token(kAlpha, bench.now());
    bench.say("ALPHA просить токен пілота", alpha_token);
    bench.say("BRAVO просить той самий токен", arbiter.request_pilot_token(kBravo, bench.now()));
    bench.say("невідома станція просить токен", arbiter.request_pilot_token(kGhost, bench.now()));
    bench.say("SENSOR (без ролі пілота) просить токен",
              arbiter.request_pilot_token(kSensor, bench.now()));

    const Token nonce_alpha = alpha_token.value_or(Token{});

    // 2. Гарячий шлях: що пропускається в мікшер, а що ні.
    bench.say("стіки ALPHA із чинним nonce", arbiter.flight_allowed(kAlpha, nonce_alpha));
    bench.say("стіки ALPHA зі старим nonce",
              arbiter.flight_allowed(kAlpha, Token{nonce_alpha.value ^ 1U}));
    bench.say("стіки BRAVO з підгляненим nonce ALPHA", arbiter.flight_allowed(kBravo, nonce_alpha));

    // 3. Розділення площин: камера й політ не заважають одне одному.
    bench.say("SENSOR веде підвіс", arbiter.payload_allowed(kSensor, bench.now()));
    bench.say("ALPHA лізе в підвіс", arbiter.payload_allowed(kAlpha, bench.now()));

    // 4. Передача зміни ALPHA -> BRAVO. Апарат висить, тяга 550.
    arbiter.set_current_thrust(550);
    bench.say("ALPHA пропонує зміну BRAVO",
              arbiter.initiate_handover(kAlpha, kBravo, bench.now()));
    bench.say("ALPHA керує далі, поки триває перевірка",
              arbiter.flight_allowed(kAlpha, nonce_alpha));

    bench.advance(100ms);
    bench.say("BRAVO: крен відхилено на 12%",
              arbiter.confirm_handover_sticks(kBravo, StickAxes{120, -8, 4, 545}, bench.now()));

    bench.advance(100ms);
    bench.say("BRAVO: стіки в центрі, газ в упорі вниз",
              arbiter.confirm_handover_sticks(kBravo, StickAxes{-14, 9, -6, 0}, bench.now()));

    bench.advance(100ms);
    bench.say("BRAVO: нейтраль і газ під тягу (перший кадр)",
              arbiter.confirm_handover_sticks(kBravo, StickAxes{-14, 9, -6, 528}, bench.now()));

    bench.advance(100ms);
    // дрейф у межах гістерезису — витримка не збивається
    bench.say("BRAVO: витримка ще не набігла",
              arbiter.confirm_handover_sticks(kBravo, StickAxes{20, -3, 11, 572}, bench.now()));

    bench.advance(300ms);
    auto bravo_token =
        arbiter.confirm_handover_sticks(kBravo, StickAxes{-22, 12, 7, 561}, bench.now());
    bench.say("BRAVO: витримка 300 мс набігла", bravo_token);
    const Token nonce_bravo = bravo_token.value_or(Token{});

    bench.say("ALPHA шле стіки після передачі", arbiter.flight_allowed(kAlpha, nonce_alpha));
    bench.say("BRAVO шле стіки з новим nonce", arbiter.flight_allowed(kBravo, nonce_bravo));

    // 5. Передача, яку ніхто не підтвердив: вікно згоряє, борт лишається за BRAVO.
    bench.say("BRAVO пропонує зміну назад ALPHA",
              arbiter.initiate_handover(kBravo, kAlpha, bench.now()));
    bench.advance(5200ms);
    bench.say("вікно передачі згоріло, ніхто не підтвердив", std::string_view{"—"});

    // 6. Асиметричне зникнення каналу: борт судить лише за власним таймером.
    bench.set_transmitting(kBravo, false);
    bench.advance(1100ms);
    bench.say("BRAVO замовк на 1.1 с", std::string_view{"—"});
    bench.say("стіки BRAVO після втрати оренди", arbiter.flight_allowed(kBravo, nonce_bravo));
    bench.say("SENSOR і далі веде підвіс", arbiter.payload_allowed(kSensor, bench.now()));

    bench.set_transmitting(kBravo, true);
    bench.advance(200ms);
    bench.say("BRAVO знову в ефірі", std::string_view{"—"});
    bench.say("стіки BRAVO зі СТАРИМ nonce", arbiter.flight_allowed(kBravo, nonce_bravo));

    // 7. Аварійне перехоплення командиром — без згоди чинного пілота.
    bench.say("SENSOR вдає командира", arbiter.commander_override(kSensor, bench.now()));

    auto cmd_token = arbiter.commander_override(kCmd, bench.now());
    bench.say("CMD перехоплює борт", cmd_token);
    const Token nonce_cmd = cmd_token.value_or(Token{});

    bench.say("стіки BRAVO під замком", arbiter.flight_allowed(kBravo, nonce_bravo));
    bench.say("стіки CMD під замком", arbiter.flight_allowed(kCmd, nonce_cmd));
    bench.say("SENSOR веде підвіс під замком", arbiter.payload_allowed(kSensor, bench.now()));
    bench.say("ALPHA просить токен під замком", arbiter.request_pilot_token(kAlpha, bench.now()));
    bench.say("BRAVO намагається зняти замок", arbiter.release_override(kBravo));
    bench.say("CMD віддає борт", arbiter.release_override(kCmd));
    bench.say("стіки CMD після зняття замка", arbiter.flight_allowed(kCmd, nonce_cmd));

    auto again = arbiter.request_pilot_token(kAlpha, bench.now());
    bench.say("ALPHA бере вільний токен", again);
    bench.say("стіки ALPHA із новим nonce",
              arbiter.flight_allowed(kAlpha, again.value_or(Token{})));

    return 0;
}
