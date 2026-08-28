#include <mutex>
#include <iostream>
#include <string>
#include <vector>
#include <memory>

class HardwareSensorCluster {
private:
    struct CalibrationProfile {
        std::vector<double> gains;
        std::string firmware_version;
    };

    std::unique_ptr<CalibrationProfile> profile_;
    std::once_flag calibration_flag_;

    void load_profile_from_eeprom(const std::string& chip_serial) {
        std::cout << "Зчитування калібрувального профілю для чіпа " << chip_serial << "...\n";
        auto p = std::make_unique<CalibrationProfile>();
        p->gains = {1.024, 0.998, 1.005};
        p->firmware_version = "v2.4.1";
        profile_ = std::move(p);
    }

public:
    HardwareSensorCluster() = default;

    void read_sensor(int channel) {
        // Лінива ініціалізація з передачею методу та аргументів
        std::call_once(calibration_flag_, &HardwareSensorCluster::load_profile_from_eeprom, 
                       this, "CHIP-XYZ-9876");

        std::cout << "Канал " << channel << " з коефіцієнтом: " 
                  << profile_->gains[channel % profile_->gains.size()] << "\n";
    }
};
