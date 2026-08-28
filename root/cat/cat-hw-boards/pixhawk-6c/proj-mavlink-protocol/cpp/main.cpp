#include <mavsdk/mavsdk.h>
#include <mavsdk/plugins/action/action.h>
#include <mavsdk/plugins/telemetry/telemetry.h>

#include <chrono>
#include <cstdint>
#include <iostream>
#include <thread>

using namespace mavsdk;
using std::chrono::seconds;
using std::this_thread::sleep_for;

int main(int argc, char** argv)
{
    if (argc != 2) {
        std::cerr << "вжиток: " << argv[0] << " <connection>\n"
                  << "  напр.  serial:///dev/ttyACM0:921600   (Linux, USB)\n"
                  << "         serial://COM3:921600            (Windows, USB)\n"
                  << "         udp://:14540                    (SITL / мостик)\n";
        return 1;
    }

    // 1) Створюємо MAVSDK у ролі наземної станції (це задасть наш sysid/compid).
    Mavsdk mavsdk{Mavsdk::Configuration{Mavsdk::ComponentType::GroundStation}};

    // 2) Відкриваємо з'єднання за URL (серійний порт, UDP чи TCP — байдуже).
    const ConnectionResult conn = mavsdk.add_any_connection(argv[1]);
    if (conn != ConnectionResult::Success) {
        std::cerr << "не вдалося відкрити з'єднання: " << conn << '\n';
        return 1;
    }

    // 3) Чекаємо HEARTBEAT — тобто поки з'явиться апарат. Доти адреси не знаємо.
    std::cout << "чекаю апарат (heartbeat)...\n";
    std::shared_ptr<System> system;
    for (int tries = 0; tries < 30 && !system; ++tries) {
        sleep_for(seconds(1));
        for (auto& s : mavsdk.systems()) {
            if (s->has_autopilot()) { system = s; break; }  // це саме автопілот
        }
    }
    if (!system) {
        std::cerr << "апарат не відповів за 30 с — перевір кабель/порт/швидкість\n";
        return 1;
    }
    std::cout << "апарат на зв'язку\n";

    // 4) Плагіни: Telemetry (читати стан) і Action (команди-дії).
    auto telemetry = Telemetry{system};
    auto action    = Action{system};

    // 5) Чекаємо, поки давачі й оцінка положення готові (health).
    //    Злітати з «попливлою» оцінкою — падіння; тому не поспішаємо.
    std::cout << "чекаю готовності давачів...\n";
    while (!telemetry.health_all_ok()) {
        sleep_for(seconds(1));
    }
    std::cout << "давачі готові\n";

    // 6) Підписуємось на висоту — колбек викликається щоразу, як прийде оновлення.
    telemetry.subscribe_position([](Telemetry::Position p) {
        std::cout << "  висота над точкою зльоту: "
                  << p.relative_altitude_m << " м\n";
    });

    // 7) Задаємо висоту зльоту й зброїмо. arm() поверне помилку, якщо не знято
    //    кнопку-запобіжник чи не пройшли передпольотні перевірки.
    action.set_takeoff_altitude(3.0f);  // 3 метри

    std::cout << "зброю...\n";
    const Action::Result arm = action.arm();
    if (arm != Action::Result::Success) {
        std::cerr << "зброїти не вдалося: " << arm
                  << "  (кнопка-запобіжник? калібрування? GPS?)\n";
        return 1;
    }

    // 8) Злітаємо. Команда лише ІНІЦІЮЄ зліт — апарат набирає висоту сам.
    std::cout << "злітаю...\n";
    const Action::Result to = action.takeoff();
    if (to != Action::Result::Success) {
        std::cerr << "зліт не вдався: " << to << '\n';
        return 1;
    }

    sleep_for(seconds(10));   // висимо 10 секунд, слухаючи телеметрію висоти

    // 9) Приземляємось і чекаємо, поки апарат справді торкнеться землі.
    std::cout << "сідаю...\n";
    const Action::Result land = action.land();
    if (land != Action::Result::Success) {
        std::cerr << "команда посадки не пройшла: " << land << '\n';
        return 1;
    }
    while (telemetry.in_air()) {          // поки в повітрі — чекаємо
        sleep_for(seconds(1));
    }
    std::cout << "сів. роззброєно автоматично.\n";
    return 0;
}
