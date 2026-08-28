#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <sstream>
#include <charconv>
#include <iomanip>

struct TestPoint {
    std::string refdes;
    std::string pin;
    double x_mm{0.0};
    double y_mm{0.0};
    bool is_smd{false};
};

struct NetlistDatabase {
    std::unordered_map<std::string, std::vector<TestPoint>> nets;

    bool parse_ipc_line(std::string_view line) {
        if (line.empty() || line.front() == 'C' || line.front() == 'P' || line.front() == '#') {
            return false;
        }

        std::istringstream stream{std::string(line)};
        int opcode = 0;
        std::string net_name, refdes, pin_raw;

        if (!(stream >> opcode >> net_name >> refdes >> pin_raw)) {
            return false;
        }

        std::string pin = (pin_raw.starts_with('-')) ? pin_raw.substr(1) : pin_raw;

        double x_val = 0.0;
        double y_val = 0.0;

        const auto x_pos = line.find("X+");
        const auto y_pos = line.find("Y+");

        if (x_pos != std::string_view::npos && x_pos + 8 <= line.size()) {
            std::from_chars(line.data() + x_pos + 2, line.data() + x_pos + 8, x_val);
            x_val /= 1000.0;
        }
        if (y_pos != std::string_view::npos && y_pos + 8 <= line.size()) {
            std::from_chars(line.data() + y_pos + 2, line.data() + y_pos + 8, y_val);
            y_val /= 1000.0;
        }

        nets[net_name].push_back(TestPoint{
            .refdes = std::move(refdes),
            .pin = std::move(pin),
            .x_mm = x_val,
            .y_mm = y_val,
            .is_smd = (opcode == 327)
        });

        return true;
    }

    void print_summary() const {
        std::cout << "=== Звіт розбору списку з'єднань (IPC-D-356) ===\n";
        std::cout << "Знайдено унікальних мереж: " << nets.size() << "\n\n";

        for (const auto& [net_name, points] : nets) {
            std::cout << "Мережа [" << net_name << "] — точок з'єднання: " << points.size() << "\n";
            for (const auto& pt : points) {
                std::cout << "  -> Вузол " << pt.refdes << "." << pt.pin
                          << " (" << (pt.is_smd ? "SMD" : "THT") << ")"
                          << " на (" << std::fixed << std::setprecision(2)
                          << pt.x_mm << ", " << pt.y_mm << ") мм\n";
            }
        }
    }
};

int main() {
    const std::string sample_ipc_data =
        "C  IPC-D-356 Test Netlist\n"
        "P  UNITS CUST\n"
        "317 VCC_3V3       U1   -14   M D0030A0050P0000X+010500Y+020000X0030Y0050\n"
        "327 VCC_3V3       C1   -1    M D0020A0040P0000X+012000Y+019500X0020Y0040\n"
        "327 VCC_3V3       R1   -2    M D0020A0040P0000X+015200Y+022100X0020Y0040\n"
        "317 GND           U1   -7    M D0030A0050P0000X+010500Y+027000X0030Y0050\n"
        "327 GND           C1   -2    M D0020A0040P0000X+012000Y+026500X0020Y0040\n"
        "317 SPI_MOSI      U1   -5    M D0030A0050P0000X+010500Y+023000X0030Y0050\n"
        "327 SPI_MOSI      R2   -1    M D0020A0040P0000X+018000Y+023000X0020Y0040\n";

    NetlistDatabase db;
    std::istringstream input_stream{sample_ipc_data};
    std::string line;

    while (std::getline(input_stream, line)) {
        db.parse_ipc_line(line);
    }

    db.print_summary();
    return 0;
}
