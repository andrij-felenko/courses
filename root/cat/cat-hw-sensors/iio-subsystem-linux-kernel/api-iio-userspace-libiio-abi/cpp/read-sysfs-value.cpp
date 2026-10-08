#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>

static double read_sysfs_value(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Помилка відкриття файла: " + path);
    }
    double value = 0.0;
    file >> value;
    return value;
}

int main() {
    const std::string base_path = "/sys/bus/iio/devices/iio:device0/";
    try {
        double raw = read_sysfs_value(base_path + "in_accel_x_raw");
        double scale = read_sysfs_value(base_path + "in_accel_x_scale");
        double offset = 0.0;
        try {
            offset = read_sysfs_value(base_path + "in_accel_x_offset");
        } catch (...) {
            // Атрибут offset може бути відсутнім, якщо зсув дорівнює 0
            offset = 0.0;
        }

        double accel_x_phys = (raw + offset) * scale;
        std::cout << "Прискорення X: " << accel_x_phys << " m/s^2\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка читання sysfs: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
