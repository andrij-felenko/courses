#include <mavsdk/mavsdk.h>
#include <mavsdk/plugins/action/action.h>
#include <mavsdk/plugins/telemetry/telemetry.h>
#include <iostream>

using namespace mavsdk;

int main() {
    Mavsdk mavsdk{Mavsdk::Configuration{Mavsdk::ComponentType::GroundStation}};

    // під'єднуємось до SITL рівно так, як під'єдналися б до справжнього дрона:
    // змінився б ЛИШЕ цей рядок (порт замість радіо) — решта коду та сама
    mavsdk.add_any_connection("udpin://127.0.0.1:14550");

    // знайомство: чекаємо, поки апарат з'явиться на лінії
    std::shared_ptr<System> system;
    while (mavsdk.systems().empty()) { /* чекаємо heartbeat */ }
    system = mavsdk.systems().at(0);
    std::cout << "апарат на лінії\n";

    Action action{system};
    Telemetry telemetry{system};

    action.set_takeoff_altitude(10.0f);      // цільова висота 10 м
    action.arm();                            // озброїти мотори (режим — автоматично GUIDED/Offboard)
    action.takeoff();                        // команда злетіти

    // стежимо за висотою з телеметрії — апарат справді «злітає» в моделі
    telemetry.subscribe_position([](Telemetry::Position pos) {
        std::cout << "висота: " << pos.relative_altitude_m << " м\n";
    });

    while (telemetry.position().relative_altitude_m < 9.5f) { /* чекаємо набору висоти */ }
    return 0;
}
