#include <iostream>
#include <array>
#include <hyperion/core.hpp>
#include <hyperion/math.hpp>

int main() {
    hyperion::Engine engine("TelemetryAlpha");
    
    constexpr std::array<double, 4> metrics = {10.5, 20.25, 5.75, 3.5};
    double total = hyperion::math::accumulate_span<double>(metrics);
    
    std::string payload = "SensorData:Total=" + std::to_string(total);
    uint32_t checksum = engine.compute_hash(payload);
    
    std::cout << "Engine: " << engine.name() << "\n";
    std::cout << "Metrics sum: " << total << "\n";
    std::cout << "Payload hash: 0x" << std::hex << checksum << std::dec << "\n";
    
    return 0;
}
