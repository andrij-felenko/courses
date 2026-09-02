#include "arbiter.hpp"
#include "gcs_session.hpp"
#include "mavlink_codec.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <format>
#include <iostream>
#include <span>
#include <vector>

/* Стенд на 3.4 секунди модельного часу: контур стабілізації 400 Гц, джойстик
 * станції 50 Гц, серцебиття 1 Гц. Сценарій — той самий політ, з якого
 * починається стаття. */

namespace {

using namespace manual_control;

constexpr std::uint8_t kOurSysid   = 1;
constexpr std::uint8_t kGcsSysid   = 255;
constexpr std::uint8_t kRogueSysid = 250;
constexpr auto kTick = std::chrono::microseconds{2500};  // 400 Гц

// Черга байтів, що йде в бортовий UART цього такту.
class RadioLink {
public:
    void push(const mavlink::Message& msg, std::uint8_t sysid, std::uint8_t& seq)
    {
        std::array<std::byte, 64> frame{};
        const std::size_t n = mavlink::encode(frame, msg, sysid, mavlink::kCompMissionPlanner, seq++);
        bytes_.insert(bytes_.end(), frame.begin(), frame.begin() + static_cast<std::ptrdiff_t>(n));
    }

    [[nodiscard]] std::span<const std::byte> drain() noexcept { return bytes_; }
    void clear() noexcept { bytes_.clear(); }

private:
    std::vector<std::byte> bytes_;
};

class GcsSimulator {
public:
    void tick(Millis t, RadioLink& radio)
    {
        if (t >= nextHeartbeat_) {  // серцебиття йде навіть тоді, коли вікно
            radio.push(mavlink::Message{mavlink::Heartbeat{
                           .customMode = 0, .type = 6, .autopilot = 8,
                           .baseMode = 0, .systemStatus = 4, .mavlinkVersion = 3}},
                       kGcsSysid, seqGcs_);  // джойстика вже не відповідає
            nextHeartbeat_ += Millis{1000};
        }

        if (t == Millis{100}) sendArm(radio, true, 0);
        if (t == Millis{200}) sendArm(radio, true, 1);
        if (t == Millis{3200}) sendArm(radio, false, 1);

        if (t == Millis{800}) {
            // Друга станція на тому ж модемі шле повний крен.
            sendManual(radio, kRogueSysid, seqRogue_, 0, 1000, 500);
        }

        if (t >= Millis{900} && t < Millis{2900}) {
            // Вікно введення джойстика зависло: черга в ОС не росте.
            nextManual_ = t + Millis{20};
            return;
        }
        if (t >= Millis{520} && t < Millis{700}) {
            // Сплеск DPC-затримки: драйвер USB-UART тримає буфер, пакети
            // чекають у черзі й вистрілять пачкою, коли ОС їх віддасть.
            return;
        }

        while (t >= nextManual_) {
            // До 640 мс — крейсерський тангаж уперед; далі оператор уже
            // відхилив стік назад на екстрене гальмування.
            const std::int16_t x = (nextManual_ >= Millis{640}) ? -1000 : 400;
            sendManual(radio, kGcsSysid, seqGcs_, x, 0, 500);
            nextManual_ += Millis{20};
        }
    }

private:
    static void sendManual(RadioLink& radio, std::uint8_t sysid, std::uint8_t& seq,
                           std::int16_t x, std::int16_t y, std::int16_t z)
    {
        radio.push(mavlink::Message{mavlink::ManualControl{
                       .x = x, .y = y, .z = z, .r = 0, .buttons = 0, .target = kOurSysid}},
                   sysid, seq);
    }

    void sendArm(RadioLink& radio, bool arm, std::uint8_t confirmation)
    {
        mavlink::CommandLong cl{};
        cl.command         = mavlink::kCmdComponentArmDisarm;
        cl.param[0]        = arm ? 1.0F : 0.0F;
        cl.targetSystem    = kOurSysid;
        cl.targetComponent = mavlink::kCompAutopilot1;
        cl.confirmation    = confirmation;
        radio.push(mavlink::Message{cl}, kGcsSysid, seqGcs_);
    }

    Millis       nextManual_{0};
    Millis       nextHeartbeat_{0};
    std::uint8_t seqGcs_{0};
    std::uint8_t seqRogue_{0};
};

// Фізичний пульт: 50 Гц, живий на початку і з 2050 мс.
class RcSimulator {
public:
    void tick(Millis t, Arbiter& arbiter)
    {
        if (t < next_)
            return;
        next_ += Millis{20};

        if (t >= Millis{400} && t < Millis{2050})
            return;  // пульт поза межею дальності — кадрів CRSF немає

        Axes rc{};
        if (t >= Millis{2100} && t < Millis{2500})
            rc.pitch = -600;  // пілот безпеки взяв керування на себе
        arbiter.feedRc(rc, t);
    }

private:
    Millis next_{0};
};

}  // namespace

int main()
{
    Arbiter arbiter;
    arbiter.setHomeAvailable(true);  // фікс є, домашня точка записана
    GcsSession session{arbiter, kOurSysid, mavlink::kCompAutopilot1};

    RadioLink    radio;
    GcsSimulator gcs;
    RcSimulator  rc;

    auto prevState = State::RcActive;  // завідомо інший, щоб перший рядок надрукувався
    auto prevFs    = FailsafeAction::ReturnToLaunch;
    bool prevArmed = true;

    std::cout << "  час  стан          FS   armed  roll pitch  yaw thr\n";

    for (auto t_us = std::chrono::microseconds{0}; t_us <= std::chrono::microseconds{3'400'000};
         t_us += kTick) {
        const auto t = std::chrono::duration_cast<Millis>(t_us);

        // 1. Радіолінія: байти з UART радіомодема.
        radio.clear();
        gcs.tick(t, radio);
        session.consume(radio.drain(), t);

        // 2. Кадри прямого пульта.
        rc.tick(t, arbiter);

        // 3. Контур стабілізації — рівний такт, незалежний від приходу пакетів.
        arbiter.update(t, std::chrono::duration_cast<Seconds>(kTick));

        if (const auto ack = session.takeAck(); !ack.empty())
            std::cout << std::format("{:5}  -> COMMAND_ACK, {} байт у модем\n", t.count(), ack.size());

        if (arbiter.state() != prevState || arbiter.failsafe() != prevFs ||
            arbiter.armed() != prevArmed) {
            const Axes& o = arbiter.output();
            std::cout << std::format("{:5}  {:<12}  {:<4} {:<5}  {:5} {:5} {:4} {:4}\n",
                                     t.count(), toString(arbiter.state()),
                                     toString(arbiter.failsafe()), arbiter.armed() ? "так" : "ні",
                                     o.roll, o.pitch, o.yaw, o.throttle);
            prevState = arbiter.state();
            prevFs    = arbiter.failsafe();
            prevArmed = arbiter.armed();
        }

        // Вікно, де видно роботу лімітера: пачка після провалу DPC.
        if (t >= Millis{700} && t < Millis{900} && t.count() % 40 == 0 &&
            t_us.count() % 1000 == 0) {
            const Axes& o = arbiter.output();
            std::cout << std::format("{:5}  ...           -    -      {:5} {:5} {:4} {:4}"
                                     "  (ціль тангажа {})\n",
                                     t.count(), o.roll, o.pitch, o.yaw, o.throttle,
                                     arbiter.gcsRaw().pitch);
        }
    }

    const auto& s = session.stats();
    const auto& l = session.linkStats();
    const auto& c = arbiter.counters();
    std::cout << "\nпідсумок:\n";
    std::cout << std::format("  кадрів прийнято      {} (CRC-помилок {}, поза діалектом {})\n",
                             l.frames, l.crcErrors, l.unknown);
    std::cout << std::format("  MANUAL_CONTROL       {}, HEARTBEAT {}, команд арму {}\n",
                             s.manual, s.heartbeats, s.armCommands);
    std::cout << std::format("  чужа станція         {} пакетів відкинуто, не наша адреса {}\n",
                             s.foreign, s.wrongTarget);
    std::cout << std::format("  перехоплень пультом  {}, деградацій {}, аварійних режимів {}\n",
                             c.preemptions, c.degradations, c.failsafes);
    return 0;
}
