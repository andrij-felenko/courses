// Демонстрація диспетчера команд на модельному часі.
//
// Кожен сценарій — реальна мережева пастка зі статті: загублений квиток і
// повтор, залп після сну, зрив на залізі, вичерпаний строк, повтор з ефіру,
// зникнення живлення посеред руху. Сервером тут працює build()/deliver(),
// прошивкою — Dispatcher::tick() у циклі.
//
// Збірка: c++ -std=c++23 -Wall -Wextra src/*.cpp -o cmddemo
// (потрібні std::expected і std::format; у C++20 з бібліотекою без <expected>
// код не збереться — саме заради нього й обрано свіжий стандарт).

#include <algorithm>
#include <array>
#include <cstddef>
#include <format>
#include <iostream>
#include <optional>
#include <span>
#include <string_view>

#include "actuator.hpp"
#include "dispatcher.hpp"
#include "journal.hpp"
#include "wire.hpp"

using namespace cmdctl;
using namespace std::chrono_literals;

namespace {

// Радіоканал: розбираємо квитанцію й друкуємо, щоб на занятті було видно,
// ЩО саме полетіло на сервер і в який момент.
class ConsoleUplink : public AckSink {
public:
    explicit ConsoleUplink(const SimClock& clock) noexcept : clock_{clock} {}

    void send(std::span<const std::byte> frame) override {
        const auto ack = parse_ack(frame);
        if (!ack) {
            std::cout << std::format("      <-- [битий кадр квитанції, {} байт]\n", frame.size());
            return;
        }
        std::cout << std::format("      <-- ACK ф{}  {:<9}  token=0x{:08X}  {}  detail={}  ({} B, t={} мс)\n",
                                 ack->phase, name(ack->state),
                                 static_cast<std::uint32_t>(ack->token & 0xFFFFFFFFu),
                                 name(ack->result), ack->detail,
                                 frame.size(), clock_.now().count());
    }

private:
    const SimClock& clock_;
};

// Пристрій як ціле. Nvm і годинник живуть зовні: FRAM і фізичний час
// переживають скидання живлення, а вміст SRAM — ні.
struct Device {
    Device(const SimClock& clock, Nvm& nvm, AckSink& sink) noexcept
        : actuator{clock}, journal{nvm}, dispatcher{clock, actuator, journal, sink} {}

    Actuator   actuator;
    Journal    journal;
    Dispatcher dispatcher;
};

std::uint32_t g_seq = 0;

// Кадр на боці сервера. Повтор — це передавання ТИХ САМИХ байтів: той самий
// токен, той самий seq, та сама контрольна сума.
Frame build(Type type, std::uint64_t token, Millis ttl, std::span<const std::byte> payload = {}) {
    Command cmd;
    cmd.type        = type;
    cmd.token       = token;
    cmd.seq         = ++g_seq;
    cmd.ttl         = ttl;
    cmd.payload_len = static_cast<std::uint8_t>(std::min(payload.size(), MaxPayload));
    std::copy_n(payload.begin(), cmd.payload_len, cmd.payload.begin());
    return encode_command(cmd);
}

void deliver(Device& dev, const Frame& frame) {
    dev.dispatcher.on_frame(frame.view());
}

// Прокрутка головного циклу прошивки: тік кожні 50 мс модельного часу.
void run_for(SimClock& clock, Device& dev, Millis span) {
    for (Millis t{0}; t < span; t += 50ms) {
        clock.advance(50ms);
        dev.dispatcher.tick();
    }
}

void banner(std::string_view text) {
    std::cout << std::format("\n=== {} ===\n", text);
}

}  // namespace

int main() {
    SimClock clock;
    Nvm nvm;                       // «FRAM»: переживає скидання живлення
    ConsoleUplink uplink{clock};
    Device dev{clock, nvm, uplink};
    dev.journal.clear();           // чистий журнал: пристрій із заводу

    std::array<std::byte, MaxPayload> pl{};

    // ── 1. Штатне перемикання реле ──────────────────────────────────────
    banner("1. Абсолютна команда: SET_RELAY(0, ON)");
    pl[0] = std::byte{0};
    pl[1] = std::byte{1};
    const Frame relay_on = build(Type::SetRelay, 0xA1A1A1A1u, 3000ms, std::span{pl}.first(2));
    deliver(dev, relay_on);
    run_for(clock, dev, 100ms);

    // ── 2. Битий кадр ───────────────────────────────────────────────────
    banner("2. Завада зіпсувала байт корисних даних");
    Frame broken = relay_on;
    broken.bytes[CommandHeader] ^= std::byte{0x40};   // сервер такого не надсилав
    deliver(dev, broken);

    // ── 3. Втрачений квиток і повтор неідемпотентної дії ────────────────
    banner("3. Доза 20 мл: повтор під час роботи і повтор після завершення");
    put_u16(pl, 20);
    const Frame dose = build(Type::DispenseMl, 0xB2B2B2B2u, 6000ms, std::span{pl}.first(2));
    deliver(dev, dose);
    run_for(clock, dev, 500ms);
    std::cout << "  (зворотний квиток загубився в ефірі — сервер шле той самий кадр)\n";
    deliver(dev, dose);                       // насос уже працює
    run_for(clock, dev, 2000ms);
    std::cout << "  (другий квиток теж загубився — сервер шле кадр утретє)\n";
    deliver(dev, dose);                       // доза давно налита: віддаємо кеш

    // ── 4. Залп накопичених команд після глибокого сну ──────────────────
    banner("4. Пробудження: брокер вистрілює трьома командами поспіль");
    put_i32(pl, 100);
    const Frame stale = build(Type::GotoPos, 0xC001u, 0ms, std::span{pl}.first(4));
    put_i32(pl, 400);
    const Frame middle = build(Type::GotoPos, 0xC002u, 4000ms, std::span{pl}.first(4));
    put_i32(pl, 250);
    const Frame fresh = build(Type::GotoPos, 0xC003u, 4000ms, std::span{pl}.first(4));
    deliver(dev, stale);
    deliver(dev, middle);
    deliver(dev, fresh);
    run_for(clock, dev, 1200ms);

    // ── 5. Зрив на залізі посеред руху ──────────────────────────────────
    banner("5. Механічна перешкода: струмовий захист");
    dev.actuator.set_obstacle(400);
    put_i32(pl, 800);
    const Frame jam = build(Type::GotoPos, 0xD00Du, 5000ms, std::span{pl}.first(4));
    deliver(dev, jam);
    run_for(clock, dev, 1500ms);
    dev.actuator.set_obstacle(std::nullopt);

    // ── 6. Строк вичерпано під час тривалої операції ─────────────────────
    banner("6. Калібрування (1500 мс) із строком життя 600 мс");
    const Frame calib = build(Type::Calibrate, 0xE1E1u, 600ms);
    deliver(dev, calib);
    run_for(clock, dev, 1000ms);

    // ── 7. Повтор з ефіру після витіснення токена з кільця ───────────────
    banner("7. Кільце змилося: заповнюємо його поточним трафіком");
    for (std::uint32_t i = 0; i < Dispatcher::RingSize; ++i) {
        const Frame noop = build(Type::Noop, 0xF0000000u + i, 2000ms);
        deliver(dev, noop);
        run_for(clock, dev, 50ms);
    }
    std::cout << "\n  (зловмисник випромінює записаний годину тому кадр SET_RELAY)\n";
    deliver(dev, relay_on);        // токена в кільці вже немає — ловить лічильник seq

    // ── 8. Зникнення живлення посеред дозування ─────────────────────────
    banner("8. Скидання живлення під час наливання");
    put_u16(pl, 30);
    const Frame big_dose = build(Type::DispenseMl, 0xE7E7E7E7u, 8000ms, std::span{pl}.first(2));
    deliver(dev, big_dose);
    run_for(clock, dev, 900ms);    // насос у роботі

    std::cout << "\n  ~~~ ЗНИКЛО ЖИВЛЕННЯ: SRAM очищено, монотонний час скинуто, FRAM цілий ~~~\n";
    dev.dispatcher.simulate_power_loss();
    dev.actuator.simulate_power_loss();
    clock.reset();
    dev.dispatcher.recover_after_reset();

    std::cout << "\n  (сервер так і не дочекався другого квитка й повторює дозу)\n";
    deliver(dev, big_dose);        // журнал урятував від другої дози
    run_for(clock, dev, 200ms);

    dev.dispatcher.print_stats();
    return 0;
}
