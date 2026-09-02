// Стендовий розбір блокувань армінгу: збірка маски з входів,
// читання її з кадру MSP_STATUS і з рядка CLI, звіт ArduPilot.

#include "ardupilot.hpp"
#include "arming_flags.hpp"
#include "msp.hpp"
#include "prearm.hpp"

#include <array>
#include <chrono>
#include <format>
#include <iostream>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace {

using namespace std::chrono_literals;

void rule(std::string_view title)
{
    std::cout << std::format("\n=== {} ===\n", title);
}

std::string hex(std::span<const std::byte> data)
{
    std::string out;
    for (const std::byte b : data) {
        out += std::format("{:02X} ", std::to_integer<unsigned>(b));
    }
    return out;
}

void scenarioBench()
{
    rule("Маска на щойно ввімкненому стенді");

    bf::StandInputs in;
    in.armSwitchHigh = true;      // тумблер Arm забули опустити після польоту
    in.accCalibrated = false;
    in.gyroCalibrating = true;
    in.throttleUs = 1180;
    in.cliOpen = true;
    in.cpuLoadPercent = 88;

    bf::PrearmMonitor monitor{in, 0ms};

    std::cout << "Одразу після подачі живлення (t=0):\n" << bf::explain(monitor.update(in, 0ms));

    // Оператор дав платі відстоятися, закрив CLI, опустив газ
    // і знизив частоту PID-циклу. Тумблер поки що піднятий.
    in.gyroCalibrating = false;
    in.accCalibrated = true;
    in.cliOpen = false;
    in.throttleUs = 1000;
    in.cpuLoadPercent = 62;
    std::cout << "\nПричини усунено, але тумблер Arm усе ще піднятий (t=3000):\n"
              << bf::explain(monitor.update(in, 3000ms));

    in.armSwitchHigh = false;
    std::cout << "\nТумблер Arm опущено (t=3100):\n" << bf::explain(monitor.update(in, 3100ms));
}

// Пульт лежить упритул до приймача: до 500 мс лінка немає взагалі,
// далі кадр губиться рівно раз на 200 мс, а з 2000 мс пульт віднесли
// на два метри й потік став чистим.
bool linkValidAt(std::chrono::milliseconds t)
{
    if (t < 500ms) {
        return false;
    }
    if (t < 2000ms) {
        return t.count() % 200 != 0;
    }
    return true;
}

std::string_view describeRx(bf::Mask mask)
{
    if (mask.test(bf::Flag::BadRxRecovery)) {
        return "FAILSAFE + BAD_RX_RECOVERY: лінк є, захисна секунда триває";
    }
    if (mask.test(bf::Flag::Failsafe)) {
        return "FAILSAFE: валідних кадрів немає";
    }
    return "радіоблокувань немає — армінг дозволено";
}

void scenarioLink()
{
    rule("Захисна секунда після відновлення лінка");

    bf::StandInputs in;
    in.rxFrameValid = false;
    bf::PrearmMonitor monitor{in, 0ms};

    std::optional<std::string_view> previous;
    for (std::chrono::milliseconds t{0}; t <= 4000ms; t += 10ms) {
        in.rxFrameValid = linkValidAt(t);
        const std::string_view state = describeRx(monitor.update(in, t));
        if (!previous || *previous != state) {
            std::cout << std::format("  t={:4} мс  {}\n", t.count(), state);
            previous = state;
        }
    }
    std::cout << "  Доки кадр губиться кожні 200 мс, відлік захисної секунди\n"
                 "  перезапускається і блокування не знімається взагалі.\n";
}

void scenarioMsp()
{
    rule("Читання маски з відповіді MSP_STATUS");

    const std::vector<std::byte> request = msp::buildRequest(msp::kStatus);
    std::cout << std::format("  запит до плати: {}\n", hex(request));

    msp::Status board;
    board.cycleTimeUs = 125;
    board.sensors = 0x0007;
    board.cpuLoadPercent = 88;
    board.gyroCycleTimeUs = 125;
    board.extraModeFlags = {std::byte{0}, std::byte{0}};
    board.armingFlagCount = static_cast<std::uint8_t>(bf::kFlagCount);
    board.armingDisable.set(bf::Flag::Throttle)
        .set(bf::Flag::Msp)
        .set(bf::Flag::CpuLoad)
        .set(bf::Flag::AccCal);

    std::vector<std::byte> frame = msp::encodeStatus(board);
    std::cout << std::format("  відповідь плати ({} байтів): {}\n", frame.size(), hex(frame));

    const auto parsed = msp::parseStatus(frame);
    if (!parsed) {
        std::cout << std::format("  розбір не вдався: {}\n", msp::describe(parsed.error()));
        return;
    }
    std::cout << std::format("  такт PID {} мкс, завантаження {}%, прапорців у прошивці {}\n",
                             parsed->cycleTimeUs, parsed->cpuLoadPercent, parsed->armingFlagCount);
    if (parsed->armingFlagCount > bf::kFlagCount) {
        std::cout << std::format("  ! прошивка знає {} прапорців, довідник — {}\n",
                                 parsed->armingFlagCount, bf::kFlagCount);
    }
    std::cout << bf::explain(parsed->armingDisable);

    // Три способи зіпсувати кадр — три різні відмови розбору.
    frame[7] ^= std::byte{0x20};
    std::cout << std::format("  побитий байт payload: {}\n",
                             msp::describe(msp::parseStatus(frame).error()));
    frame[7] ^= std::byte{0x20};
    std::cout << std::format("  обрізаний буфер:      {}\n",
                             msp::describe(msp::parseStatus(
                                 std::span{frame}.first(frame.size() - 3)).error()));

    // Стара прошивка віддає коротший payload: сума збігається,
    // але до armingDisableFlags полів не вистачає.
    msp::Status old = board;
    old.extraModeFlags.clear();
    std::vector<std::byte> shortFrame = msp::encodeStatus(old);
    shortFrame.resize(5 + 8 + 1);
    shortFrame[3] = std::byte{8};
    std::uint8_t crc = static_cast<std::uint8_t>(8u ^ msp::kStatus);
    for (std::size_t i = 0; i < 8; ++i) {
        crc ^= std::to_integer<std::uint8_t>(shortFrame[5 + i]);
    }
    shortFrame.back() = std::byte{crc};
    std::cout << std::format("  короткий payload:     {}\n",
                             msp::describe(msp::parseStatus(shortFrame).error()));
}

void scenarioCli()
{
    rule("Розбір рядка CLI-команди status");

    constexpr std::string_view line =
        "Arming disable flags: THROTTLE CLI MSP RPMFILTER SUPERGLUE";
    const auto parsed = bf::parseCliStatus(line);
    if (!parsed) {
        std::cout << std::format("  {}\n", bf::describe(parsed.error()));
        return;
    }
    std::cout << std::format("  вхід: {}\n", line);
    std::cout << std::format("  маска 0x{:08X}, нерозпізнаних назв: {}\n",
                             parsed->mask.raw(), parsed->unknownNames.size());
    for (const std::string& name : parsed->unknownNames) {
        std::cout << std::format("    невідома назва: {}\n", name);
    }
    std::cout << bf::explain(parsed->mask);

    const auto clean = bf::parseCliStatus("Arming disable flags: None");
    std::cout << "\n  вхід: Arming disable flags: None\n" << bf::explain(clean->mask);

    const auto broken = bf::parseCliStatus("# rateprofile 0");
    std::cout << std::format("  чужий рядок: {}\n", bf::describe(broken.error()));
}

void scenarioArduPilot()
{
    rule("ArduPilot: ARMING_CHECK і повідомлення STATUSTEXT");

    const std::array failing{ap::Check::Compass, ap::Check::Gps,
                             ap::Check::BoardVoltage, ap::Check::HardwareSwitch};

    const auto print = [](const std::vector<ap::StatusText>& report) {
        for (const ap::StatusText& msg : report) {
            std::cout << std::format("    [severity={}] {}\n",
                                     static_cast<unsigned>(msg.severity()), msg.text());
        }
    };

    std::cout << "  ARMING_CHECK = 1 (усі перевірки):\n";
    print(ap::prearmReport(ap::CheckMask{1}, failing));

    // Для столу знімають GPS: біт All гасять, решту бітів ставлять руками.
    constexpr std::int32_t stand = 0x7FFE &
                                   ~(1 << static_cast<int>(ap::Check::Gps)) &
                                   ~(1 << static_cast<int>(ap::Check::GpsConfig));
    std::cout << std::format("\n  ARMING_CHECK = {} (усе, крім GPS):\n", stand);
    print(ap::prearmReport(ap::CheckMask{stand}, failing));

    std::cout << "\n  вимкнені параметром перевірки:";
    for (std::size_t i = 1; i < ap::kCheckCount; ++i) {
        const auto check = static_cast<ap::Check>(i);
        if (!ap::CheckMask{stand}.enabled(check)) {
            std::cout << std::format(" {};", ap::info(check).name);
        }
    }
    std::cout << "\n  Порожній звіт означає дозвіл на армінг.\n";
}

}  // namespace

int main()
{
    scenarioBench();
    scenarioLink();
    scenarioMsp();
    scenarioCli();
    scenarioArduPilot();
    return 0;
}
