#include <mavsdk/mavsdk.h>
#include <mavsdk/plugins/action/action.h>
#include <mavsdk/plugins/telemetry/telemetry.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <memory>

using namespace mavsdk;

int main() {
    std::cout << "[SITL Client] Ініціалізація зв'язку з симулятором через MAVSDK...\n";

    Mavsdk mavsdk{Mavsdk::Configuration{Mavsdk::ComponentType::GroundStation}};

    // Підключення до локального порту SITL
    ConnectionResult connection_result = mavsdk.add_any_connection("udp://:14540");
    if (connection_result != ConnectionResult::Success) {
        std::cerr << "Помилка відкриття сокета: " << connection_result << "\n";
        return 1;
    }

    // Очікування виявлення апарата за пакетом Heartbeat
    std::cout << "Очікування підключення автопілота...\n";
    while (mavsdk.systems().empty()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    auto system = mavsdk.systems().at(0);
    auto telemetry = std::make_shared<Telemetry>(system);
    auto action = std::make_shared<Action>(system);

    // Підписка на оновлення телеметрії польоту
    telemetry->subscribe_position([](Telemetry::Position position) {
        std::cout << "[Телеметрія] Висота: " << position.relative_altitude_m 
                  << " м | Широта: " << position.latitude_deg 
                  << " | Довгота: " << position.longitude_deg << "\n";
    });

    // Очікування готовності навігаційного фільтра EKF до польоту
    while (!telemetry->health().is_armable) {
        std::cout << "Очікування ініціалізації EKF та фіксації GNSS...\n";
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    std::cout << "Озброєння моторів (Arming)...\n";
    action->arm();

    std::cout << "Команда зльоту на висоту 15 метрів...\n";
    action->set_takeoff_altitude(15.0f);
    action->takeoff();

    std::this_thread::sleep_for(std::chrono::seconds(10));

    std::cout << "Повернення додому (RTL)...\n";
    action->return_to_launch();

    std::this_thread::sleep_for(std::chrono::seconds(5));
    return 0;
}
