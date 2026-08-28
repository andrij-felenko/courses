#include <telemetry/telemetry.hpp>
#include <iostream>
#include <array>

int main() {
    telemetry::PacketEncoder encoder("engine_chamber_01");
    
    std::array<telemetry::SensorRecord, 2> records{{
        {101, 1718900000000ULL, 42.5},
        {102, 1718900001000ULL, 120.3}
    }};

    auto payload = encoder.encode(records);
    std::cout << "Успішно закодовано байтів: " << payload.size() << "\n";
    return payload.empty() ? 1 : 0;
}
