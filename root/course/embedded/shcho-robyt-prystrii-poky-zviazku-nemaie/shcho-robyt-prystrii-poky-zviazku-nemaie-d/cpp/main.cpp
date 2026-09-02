#include <chrono>
#include <cmath>
#include <cstdint>
#include <print>
#include <string_view>

#include "controller.hpp"
#include "hardware.hpp"
#include "link.hpp"

namespace {

using namespace cart;

constexpr std::uint32_t kKey           = 0x00C0FFEEu;
constexpr std::uint32_t kSessionFirst  = 0x000051E5u;
constexpr std::uint32_t kSessionSecond = 0x00007A11u;
constexpr Millis        kFramePeriod   = 40ms;
constexpr Millis        kSimEnd        = 95s;

// Годинник пульта попереду нашого на 3.2 с, а перед перепідключенням сервер
// сам підтягнувся по NTP назад на 1.5 с. Пристрій мусить пережити обидва
// зсуви, жодного разу не пустивши свій монотонний час назад.
Millis serverClock(Millis t) noexcept { return t < 70s ? t + 3200ms : t + 1700ms; }

// Ефір: коротке завмирання за стелажем і довгий обрив за бетонною стіною.
bool airUp(Millis t) noexcept {
    if (t >= 3s && t < 3300ms) return false;
    if (t >= 6s && t < 76s) return false;
    return true;
}

float pultThrottle(Millis t) noexcept { return t < 2s ? 0.4f : 0.8f; }

std::uint32_t rng = 2463534242u;
float sensorNoise() noexcept {
    rng ^= rng << 13;
    rng ^= rng >> 17;
    rng ^= rng << 5;
    return (static_cast<float>(rng % 1000u) / 1000.0f - 0.5f) * 0.6f;
}

void report(Millis t, const Board& board, const FallbackController& fsm, std::string_view why) {
    std::println("{:7.2f} с | {:<16} | {:<20} | тяга {:+5.2f} | ШІМ {:+5.2f} | живлення {:d} | interlock {:d} | гальмо {:d} | лог {:3}",
                 t.count() / 1000.0, why, describe(fsm.state()), fsm.throttle(), board.throttleOut(),
                 board.powered(), board.interlock(), board.brake(), fsm.log().pending());
}

}  // namespace

int main() {
    Board board;
    FallbackController fsm{board, kKey};

    std::uint32_t session = kSessionFirst;
    std::uint32_t seq = 1;
    bool handshaken = false;
    bool airPrev = false;
    State statePrev = fsm.state();
    Millis nextFrame{0};
    Millis nextNote = 10s;

    Frame staleFrame{};
    bool staleSaved = false;
    bool staleTried = false;

    report(board.now(), board, fsm, "старт");

    for (Millis t{0}; t <= kSimEnd; t += kTick) {
        const bool air = airUp(t);
        if (air != airPrev) {
            board.setRadioUp(air);
            if (!air) handshaken = false;
            else if (t > 10s) session = kSessionSecond;   // після довгої тиші пульт відкриває нову сесію
            airPrev = air;
            report(t, board, fsm, air ? "ефір є" : "ефір зник");
        }

        if (air && t >= nextFrame) {
            nextFrame = t + kFramePeriod;
            const auto stamp = serverClock(t);

            if (!handshaken) {
                // Крок 1: спершу пульт виплюне команду, що чекала в його черзі
                // ще з часів до обриву. Пристрій зобов'язаний її відкинути.
                if (staleSaved && !staleTried && t > 70s) {
                    staleTried = true;
                    const auto verdict = fsm.handleFrame(staleFrame);
                    std::println("{:7.2f} с | {:<16} | застаріла команда з черги пульта: {}",
                                 t.count() / 1000.0, "реплей",
                                 verdict ? std::string_view{"прийнято"} : describe(verdict.error()));
                }
                if (fsm.handleFrame(Link::makeHello(kKey, session, stamp))) {
                    handshaken = true;
                    report(t, board, fsm, "рукостискання");
                }
            } else {
                const auto frame = Link::makeCommand(kKey, session, seq++, stamp, pultThrottle(t), 0.0f);
                (void)fsm.handleFrame(frame);
                if (!staleSaved && t >= 2s) {
                    staleFrame = frame;
                    staleSaved = true;
                }
            }
        }

        // Давач струму двигуна: те, що справді доїхало до обмоток, плюс шум.
        fsm.tick(std::fabs(board.throttleOut()) * 42.0f + sensorNoise());

        if (fsm.state() != statePrev) {
            statePrev = fsm.state();
            report(t, board, fsm, "зміна стану");
        }
        if (t >= nextNote) {
            nextNote += 10s;
            report(t, board, fsm, "зріз");
        }

        board.advance(kTick);
    }

    const auto& rejects = fsm.link().rejects();
    const auto& stats = fsm.log().stats();

    std::println("\n--- підсумок прогону ---");
    std::println("стан наприкінці         : {}", describe(fsm.state()));
    std::println("кадрів прийнято         : {}", fsm.link().accepted());
    std::println("відкинуто               : CRC {}, автентифікація {}, сесія {}, повтор {}, застарілі {}",
                 rejects.crc, rejects.auth, rejects.session, rejects.replay, rejects.stale);
    std::println("спрацювань мертвої руки : {}", fsm.deadman().trips());
    std::println("записів у Flash         : {} (затерто не злитих {}, втрачено {}, блокувальних стирань {})",
                 stats.written, stats.overwritten, stats.dropped, stats.blockingErases);
    std::println("у черзі на злив         : {} записів, в ефір пішло {} байтів",
                 fsm.log().pending(), board.bytesSent());
    std::println("поправка годинника      : {:+} мс, лишилося підтягнути {:+} мс",
                 fsm.clock().offset().count(), fsm.clock().pending().count());

    std::print("стирань по секторах     :");
    for (std::size_t i = 0; i < kSectorCount; ++i) std::print(" {}", board.eraseCount(i));
    std::println("");

    const auto crash = fsm.log().crashRecords();
    std::println("чорна скринька ({} записів):", crash.size());
    for (const auto& r : crash)
        std::println("   t={:8.2f} с  подія 0x{:02X}  {}", r.stamp.count() / 1000.0, r.event,
                     event::describe(r.event));
    return 0;
}
