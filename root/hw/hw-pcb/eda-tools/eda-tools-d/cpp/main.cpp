#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <format>

struct EdaPinRecord {
    std::string refdes;
    std::string pin;
    std::string net_name;
    double x_mm{0.0};
    double y_mm{0.0};
};

void filter_net_pins(const std::vector<EdaPinRecord>& records, std::string_view target_net) {
    std::cout << "Pins connected to net [" << target_net << "]:\n";
    for (const auto& rec : records) {
        if (rec.net_name == target_net) {
            std::cout << "  Node " << rec.refdes << "." << rec.pin
                      << " at (" << rec.x_mm << ", " << rec.y_mm << ") mm\n";
        }
    }
}

int main() {
    const std::vector<EdaPinRecord> pins = {
        {"U1", "14", "VCC_3V3", 10.50, 20.00},
        {"C1", "1",  "VCC_3V3", 12.00, 19.50},
        {"R1", "2",  "VCC_3V3", 15.20, 22.10},
        {"U1", "7",  "GND",     10.50, 27.00},
        {"C1", "2",  "GND",     12.00, 26.50}
    };

    filter_net_pins(pins, "VCC_3V3");
    return 0;
}
