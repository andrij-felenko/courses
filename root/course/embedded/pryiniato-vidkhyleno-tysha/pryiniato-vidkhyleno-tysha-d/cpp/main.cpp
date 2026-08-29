// Сценарії заняття: три відповіді на команду й пастка повторного виконання.
// Час віртуальний — цикл крокує по 5 мс, тож увесь прогін триває мілісекунди.
//
// Збірка: g++ -std=c++17 -O1 main.cpp command_client.cpp sim_vehicle.cpp -o cmddemo

#include "command_client.h"
#include "sim_vehicle.h"

#include <chrono>
#include <iostream>
#include <stdexcept>

namespace {

using Clock     = std::chrono::steady_clock;
using TimePoint = Clock::time_point;

constexpr std::chrono::milliseconds kStep{5};
constexpr int                       kMaxSteps = 4000;  // 20 с віртуального часу

int failures = 0;

void check(bool condition, const char* what) {
    std::cout << (condition ? "  ✔ " : "  ✘ ") << what << "\n";
    if (!condition) {
        ++failures;
    }
}

void title(const char* text) {
    std::cout << "\n=== " << text << " ===\n";
}

// Проганяє одну транзакцію до термінального стану автомата.
template <class Frame>
Outcome execute(CommandClient& client, SimRadio& radio, TimePoint& now, const Frame& frame) {
    Outcome outcome{};
    bool    done = false;

    radio.tick(now);
    const bool started = client.send(
        now, frame,
        [&](const Outcome& result) {
            outcome = result;
            done    = true;
        },
        [](std::uint8_t progress) {
            std::cout << "  [прогрес] " << static_cast<int>(progress) << "%\n";
        });

    if (!started) {
        // Саме так інтерфейс оператора мовчки ковтає повторні натискання кнопки.
        throw std::runtime_error("канал зайнятий попередньою транзакцією");
    }

    for (int step = 0; !done && step < kMaxSteps; ++step) {
        now += kStep;
        radio.tick(now);
        client.tick(now);
    }
    if (!done) {
        throw std::runtime_error("автомат не дійшов до термінального стану");
    }

    std::cout << "  => " << state_name(outcome.state) << " / " << result_name(outcome.result)
              << ", кадрів у ефір: " << outcome.attempts << ", " << outcome.message << "\n";
    return outcome;
}

CommandLong arm_command(bool arm) {
    CommandLong frame;
    frame.command  = mav_cmd::ComponentArmDisarm;
    frame.param[0] = arm ? 1.0f : 0.0f;
    return frame;
}

CommandLong set_mode_command(std::int32_t custom_mode) {
    CommandLong frame;
    frame.command  = mav_cmd::DoSetMode;
    frame.param[0] = kCustomModeEnabled;
    frame.param[1] = static_cast<float>(custom_mode);
    return frame;
}

CommandLong gripper_toggle_command() {
    CommandLong frame;
    frame.command  = mav_cmd::DoGripper;
    frame.param[0] = 1.0f;  // номер захоплення
    frame.param[1] = 2.0f;  // перемкнути — неідемпотентна дія
    return frame;
}

}  // namespace

int main() {
    SimAutopilot vehicle;
    SimRadio     radio(vehicle, std::chrono::milliseconds(60), std::chrono::milliseconds(60));
    CommandClient client(radio, 255, 190, std::chrono::milliseconds(800), 3);
    radio.attach(client);

    TimePoint now = Clock::now();

    try {
        title("1. Відхилено: ARM без супутникового фіксу");
        Outcome out = execute(client, radio, now, arm_command(true));
        check(out.state == TxState::Rejected && out.result == MavResult::Denied,
              "борт відповів DENIED, автомат зупинився без повторів");
        check(out.attempts == 1, "відмова остаточна: другий кадр в ефір не пішов");
        check(!vehicle.armed(), "мотори лишилися вимкненими");

        title("2. Прийнято: ARM із фіксом, двічі поспіль");
        vehicle.set_gps_fix(true);
        execute(client, radio, now, arm_command(true));
        out = execute(client, radio, now, arm_command(true));
        check(out.result == MavResult::Accepted && vehicle.armed(),
              "ідемпотентна команда: повторне виконання нічого не зламало");

        title("3. Тиша в Uplink: перший кадр загинув, повтор із confirmation=1");
        radio.drop_next_uplink(1);
        out = execute(client, radio, now, set_mode_command(copter_mode::Guided));
        check(out.result == MavResult::Accepted && out.attempts == 2,
              "друга спроба дійшла, режим перемкнено");
        check(vehicle.mode() == copter_mode::Guided, mode_name(vehicle.mode()));

        title("4. Тимчасова відмова: AUTO поки не звівся EKF");
        vehicle.set_ekf_ready(false);
        out = execute(client, radio, now, set_mode_command(copter_mode::Auto));
        check(out.result == MavResult::TemporarilyRejected,
              "TEMPORARILY_REJECTED: повторити варто, але вже рішенням оператора");
        vehicle.set_ekf_ready(true);

        title("5. Тиша в Downlink: замок і кеш дедуплікації на борту");
        const int before = vehicle.gripper_actuations();
        radio.drop_next_downlink(1);  // дія виконана, квитанція загинула
        out = execute(client, radio, now, gripper_toggle_command());
        check(out.result == MavResult::Accepted && out.attempts == 2,
              "станція отримала квитанцію лише з другої спроби");
        check(vehicle.gripper_actuations() - before == 1,
              "сервопривід спрацював РІВНО один раз — кеш упізнав confirmation=1");

        title("6. Той самий сценарій без дедуплікації — подвійне спрацювання");
        vehicle.set_dedup(false);
        const int before_nodedup = vehicle.gripper_actuations();
        radio.drop_next_downlink(1);
        execute(client, radio, now, gripper_toggle_command());
        check(vehicle.gripper_actuations() - before_nodedup == 2,
              "без кешу замок клацнув двічі: вантаж скинуто й механізм закрито");
        vehicle.set_dedup(true);

        title("7. Контейнер: навігаційний наказ через LONG і через INT");
        CommandLong wrong;
        wrong.command = mav_cmd::NavLoiterUnlim;
        out = execute(client, radio, now, wrong);
        check(out.result == MavResult::CommandIntOnly,
              "COMMAND_INT_ONLY: координати у float32 борт не приймає");

        CommandInt loiter;
        loiter.command = mav_cmd::NavLoiterUnlim;
        loiter.frame   = MavFrame::GlobalRelativeAltInt;
        loiter.x       = deg_to_1e7(50.4501234);
        loiter.y       = deg_to_1e7(30.5234567);
        loiter.z       = 80.0f;
        out = execute(client, radio, now, loiter);
        check(out.result == MavResult::Accepted, "COMMAND_INT прийнято, крок координати — 1.1 см");

        title("8. Довга операція: IN_PROGRESS відсуває таймаут");
        CommandLong calibrate;
        calibrate.command = mav_cmd::DoStartMagCal;
        out = execute(client, radio, now, calibrate);
        check(out.result == MavResult::Accepted && out.attempts == 1,
              "калібрування тривало довше за таймаут, але повторів не було");

        title("9. Повна тиша: борт не відповідає");
        vehicle.set_powered(false);
        out = execute(client, radio, now, set_mode_command(copter_mode::Rtl));
        check(out.state == TxState::TimeoutFailure && out.attempts == 4,
              "після 1 + 3 спроб оголошено збій каналу керування");
        check(vehicle.mode() == copter_mode::Guided,
              "стан апарата станції невідомий — телеметрію тут не замінити нічим");
    } catch (const std::exception& error) {
        std::cerr << "збій сценарію: " << error.what() << "\n";
        return 2;
    }

    std::cout << "\nневдалих перевірок: " << failures << "\n";
    return failures == 0 ? 0 : 1;
}
