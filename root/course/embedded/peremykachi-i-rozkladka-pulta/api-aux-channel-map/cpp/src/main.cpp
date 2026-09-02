#include <chrono>
#include <format>
#include <iostream>
#include <span>
#include <utility>

#include "rc/arming.hpp"
#include "rc/channels.hpp"
#include "rc/protocol.hpp"
#include "rc/switches.hpp"

// Сценарій з теми: передавач шле канали в порядку TAER, а польотний
// контролер налаштований на AETR. Пілот рухає стік тангажу — контролер
// бачить газ. Далі — втрата лінку й поведінка приймача.

namespace {

using namespace std::chrono_literals;

constexpr auto kFramePeriod = 4ms;  // 250 Гц, типово для ExpressLRS
constexpr std::size_t kArmChannel  = rc::auxIndex(1);  // AUX1 = CH5
constexpr std::size_t kModeChannel = rc::auxIndex(2);  // AUX2 = CH6

void printAxes(std::string_view title, rc::ChannelMap map, const rc::MicrosChannels& us)
{
    const rc::AxisSet axes = rc::applyMap(map, us);
    std::cout << std::format("  {:<34} [{}] крен={:4}  тангаж={:4}  курс={:4}  ГАЗ={:4} мкс\n",
                             title, rc::mapName(map),
                             axes[std::to_underlying(rc::Axis::Roll)],
                             axes[std::to_underlying(rc::Axis::Pitch)],
                             axes[std::to_underlying(rc::Axis::Yaw)],
                             axes[std::to_underlying(rc::Axis::Throttle)]);
}

// Рядок журналу Blackbox: сирі канали, нормалізовані команди, маска режиму
void blackboxLine(std::chrono::milliseconds t, const rc::MicrosChannels& us,
                  const rc::AxisSet& axes, rc::FlightMode mode)
{
    constexpr float rateDps = 200.0f;  // типова швидкість у режимі Acro
    auto command = [](std::uint16_t v) {
        return (static_cast<float>(v) - 1500.0f) / 500.0f * rateDps;
    };
    const float throttle = (static_cast<float>(axes[std::to_underlying(rc::Axis::Throttle)]) -
                            static_cast<float>(rc::kUsMin)) /
                           static_cast<float>(rc::kUsMax - rc::kUsMin);

    std::cout << std::format(
        "BB {:5} мс  rcData={},{},{},{},{},{}  rcCommand={:+.0f}/{:+.0f}/{:+.0f} град/с, "
        "газ {:.2f}  flightModeFlags=0x{:04X}\n",
        t.count(), us[0], us[1], us[2], us[3], us[4], us[5],
        command(axes[std::to_underlying(rc::Axis::Roll)]),
        command(axes[std::to_underlying(rc::Axis::Pitch)]),
        command(axes[std::to_underlying(rc::Axis::Yaw)]),
        throttle, rc::modeFlags(mode));
}

void demoChannelOrderMismatch()
{
    std::cout << "=== 1. Розкладка передавача TAER, контролера — AETR ===\n";

    rc::RawChannels raw{};
    raw.fill(rc::kRawCenter);

    // Передавач у порядку TAER: CH1 газ, CH2 крен, CH3 тангаж, CH4 курс.
    // Пілот тримає газ унизу й штовхає стік тангажу вперед.
    raw[0] = rc::usToRaw(rc::kUsMin);
    raw[1] = rc::usToRaw(1500);
    raw[2] = rc::usToRaw(rc::kUsMax);
    raw[3] = rc::usToRaw(1500);
    raw[kArmChannel]  = rc::usToRaw(2000);
    raw[kModeChannel] = rc::usToRaw(rc::nominalUs(rc::FlightMode::Stabilize));

    rc::crsf::RcFrame frame = rc::crsf::buildRcChannels(raw);
    std::cout << std::format("  кадр CRSF, {} байтів, CRC8=0x{:02X}:", frame.size(), frame.back());
    for (std::uint8_t byte : frame) {
        std::cout << std::format(" {:02X}", byte);
    }
    std::cout << '\n';

    const auto decoded = rc::crsf::parseRcChannels(frame);
    if (!decoded) {
        std::cout << std::format("  розбір не вдався: {}\n", rc::describe(decoded.error()));
        return;
    }

    const rc::MicrosChannels us = rc::toMicros(*decoded);
    printAxes("як задумав пілот:", rc::ChannelMap::TAER, us);
    printAxes("як зрозумів контролер:", rc::ChannelMap::AETR, us);
    std::cout << "  зсув на один канал — і рух тангажем дає 100% газу, а скидання газу — крен.\n";

    // Той самий кадр із зіпсованим байтом: CRC не пускає сміття далі
    rc::crsf::RcFrame broken = frame;
    broken[7] ^= 0x20;
    const auto bad = rc::crsf::parseRcChannels(broken);
    std::cout << std::format("  кадр із перевернутим бітом: {}\n",
                             bad ? "прийнято (так не буває)" : rc::describe(bad.error()));
}

void demoSwitchHysteresis()
{
    std::cout << "\n=== 2. Гістерезис тумблера ARM (AUX1) і селектор режимів (AUX2) ===\n";

    rc::TwoPositionSwitch armSwitch;
    for (std::uint16_t us : {1000, 1340, 1380, 1500, 1620, 1660, 1200}) {
        std::cout << std::format("  AUX1 = {:4} мкс -> {}\n", us, rc::name(armSwitch.update(us)));
    }
    std::cout << std::format("  перемикань за прогін: {} (смуга 1350..1650 мкс гасить брязкіт)\n",
                             armSwitch.transitions());

    rc::ThreePositionSwitch three;
    const auto center = rc::name(three.update(1500));
    const auto held   = rc::name(three.update(1320));
    std::cout << std::format("  3-позиційний на 1500 мкс -> {}, на 1320 мкс -> {} "
                             "(проміжок між вікнами утримує позицію)\n", center, held);

    for (std::size_t i = 0; i < rc::kFlightModeCount; ++i) {
        const auto mode = static_cast<rc::FlightMode>(i);
        const auto decoded = rc::modeFromUs(rc::nominalUs(mode));
        std::cout << std::format("  AUX2 = {:4} мкс -> {:<9}  GNSS {}\n",
                                 rc::nominalUs(mode), rc::name(decoded),
                                 rc::requiresGnss(decoded) ? "потрібен" : "не потрібен");
    }
}

void demoArming()
{
    std::cout << "\n=== 3. Блокування запуску двигунів ===\n";

    rc::ArmingChecker checker{true};  // тумблер ARM стояв угорі ще до живлення

    rc::VehicleState state{
        .throttleUs     = 1500,  // газ «по центру» — наслідок чужої розкладки
        .failsafeActive = false,
        .prearmEngaged  = false,
        .armSwitch      = true,
        .calibrating    = true,
        .tiltDeg        = 31.0f,
        .compassHealthy = false,
        .gnssFix3d      = false,
        .hdop           = 3.2f,
        .mode           = rc::FlightMode::Loiter,
    };

    rc::ArmBlock blocks = rc::ArmBlock::None;
    bool armed = checker.update(state, blocks);
    std::cout << std::format("  маска блокувань = 0x{:04X}, armed = {}\n",
                             std::to_underlying(blocks), armed ? "так" : "ні");
    std::cout << std::format("  STATUSTEXT: {}\n", rc::statusText(blocks));

    for (std::uint16_t bit = 0x0001; bit <= 0x0080; bit = static_cast<std::uint16_t>(bit << 1)) {
        const auto flag = static_cast<rc::ArmBlock>(bit);
        if (any(blocks & flag)) {
            std::cout << std::format("    {:<30} 0x{:04X}\n", rc::flagName(flag), bit);
        }
    }

    // Пілот усе виправив: тумблер униз (знімає засувку), газ на мінімум,
    // апарат вирівняно, датчики готові.
    state.armSwitch = false;
    checker.update(state, blocks);

    state.armSwitch      = true;
    state.throttleUs     = rc::kUsMin;
    state.calibrating    = false;
    state.prearmEngaged  = true;
    state.tiltDeg        = 1.4f;
    state.compassHealthy = true;
    state.gnssFix3d      = true;
    state.hdop           = 0.9f;

    armed = checker.update(state, blocks);
    std::cout << std::format("  після усунення причин: маска = 0x{:04X}, armed = {}\n",
                             std::to_underlying(blocks), armed ? "так" : "ні");
}

void demoFailsafe()
{
    std::cout << "\n=== 4. Втрата лінку: таймаут 100 мс і політика приймача ===\n";

    rc::LinkMonitor link{rc::ChannelMap::AETR, rc::FailsafePolicy::PresetValues, kModeChannel};

    rc::RawChannels raw{};
    raw.fill(rc::kRawCenter);
    raw[rc::channelIndex(rc::ChannelMap::AETR, rc::Axis::Throttle)] = rc::usToRaw(1700);
    raw[kModeChannel] = rc::usToRaw(rc::nominalUs(rc::FlightMode::AltHold));

    const float sampleHz = 1000.0f / static_cast<float>(kFramePeriod.count());
    rc::Biquad rollLpf{40.0f, sampleHz};
    rc::Biquad pitchLpf{40.0f, sampleHz};

    auto now = 0ms;
    for (unsigned frameNo = 0; frameNo < 40; ++frameNo, now += kFramePeriod) {
        if (frameNo < 10) {
            link.onFrame(raw, now, false);
        }
        const bool failsafe = link.tick(now);

        rc::AxisSet axes = rc::applyMap(rc::ChannelMap::AETR, link.channelsUs());

        // Мертва зона й згладжування — саме в такому порядку, як у стеку
        auto& roll  = axes[std::to_underlying(rc::Axis::Roll)];
        auto& pitch = axes[std::to_underlying(rc::Axis::Pitch)];
        roll  = static_cast<std::uint16_t>(rollLpf(rc::applyDeadband(roll, 4)));
        pitch = static_cast<std::uint16_t>(pitchLpf(rc::applyDeadband(pitch, 4)));

        const auto mode = rc::modeFromUs(link.channelsUs()[kModeChannel]);

        if (frameNo == 9 || frameNo == 10 || frameNo == 35) {
            std::cout << (failsafe ? "  FAILSAFE " : "           ");
            blackboxLine(now, link.channelsUs(), axes, mode);
        }
    }

    // Той самий обрив, але приймач у режимі Hold Last State
    rc::LinkMonitor hold{rc::ChannelMap::AETR, rc::FailsafePolicy::HoldLastState, kModeChannel};
    hold.onFrame(raw, 0ms, false);
    hold.tick(200ms);
    std::cout << std::format(
        "  Hold Last State: газ лишився {} мкс — апарат летить за вектором до удару\n",
        hold.channelsUs()[rc::channelIndex(rc::ChannelMap::AETR, rc::Axis::Throttle)]);
}

void demoSbusFlags()
{
    std::cout << "\n=== 5. Прапорці кадру SBUS ===\n";

    rc::sbus::Packet tx{};
    tx.channels.fill(rc::kRawCenter);
    tx.channels[0] = rc::usToRaw(rc::kUsMax);
    tx.ch17      = true;
    tx.frameLost = true;
    tx.failsafe  = true;

    rc::sbus::Frame frame = rc::sbus::build(tx);

    if (const auto rx = rc::sbus::parse(frame); rx) {
        std::cout << std::format("  кадр прийнято; байт прапорців = 0x{:02X}\n", frame[23]);
        std::cout << std::format("  CH1 = {} мкс, CH17 = {}, frame_lost = {}, failsafe = {}\n",
                                 rc::rawToUs(rx->channels[0]), rx->ch17, rx->frameLost,
                                 rx->failsafe);
    } else {
        std::cout << std::format("  розбір не вдався: {}\n", rc::describe(rx.error()));
    }

    frame[0] = 0x00;  // зсув по байтах на шині — заголовок зник
    const auto broken = rc::sbus::parse(frame);
    std::cout << std::format("  кадр без заголовка: {}\n",
                             broken ? "прийнято (так не буває)" : rc::describe(broken.error()));
}

}  // namespace

int main()
{
    demoChannelOrderMismatch();
    demoSwitchHysteresis();
    demoArming();
    demoFailsafe();
    demoSbusFlags();
    return 0;
}
