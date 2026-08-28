#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <iomanip>

struct BomItem {
    std::string mpn;
    bool is_dnp{false};
    bool found_in_cpl{false};
};

struct CplItem {
    double x{0.0};
    double y{0.0};
    double rotation{0.0};
    std::string layer;
    bool found_in_bom{false};
};

static std::string trim(std::string_view str) {
    size_t first = str.find_first_not_of(" \t\r\n\"");
    if (first == std::string_view::npos) return "";
    size_t last = str.find_last_not_of(" \t\r\n\"");
    return std::string(str.substr(first, last - first + 1));
}

static std::string to_upper(std::string_view s) {
    std::string out(s);
    std::transform(out.begin(), out.end(), out.begin(), [](unsigned char c) {
        return static_cast<char>(std::toupper(c));
    });
    return out;
}

int main(int argc, char** argv) {
    const std::string bom_file = (argc > 1) ? argv[1] : "bom.csv";
    const std::string cpl_file = (argc > 2) ? argv[2] : "cpl.csv";

    std::unordered_map<std::string, BomItem> bom_map;
    std::unordered_map<std::string, CplItem> cpl_map;

    // Зчитування BOM
    std::ifstream bom_stream(bom_file);
    if (!bom_stream.is_open()) {
        std::cerr << "Помилка: не вдалося відкрити BOM файл: " << bom_file << "\n";
        return 2;
    }

    std::string line;
    bool is_first = true;
    while (std::getline(bom_stream, line)) {
        if (line.empty() || is_first) {
            is_first = false;
            continue;
        }
        std::stringstream ss(line);
        std::string des_field, mpn, pkg, dnp_str;
        if (!std::getline(ss, des_field, ',')) continue;
        std::getline(ss, mpn, ',');
        std::getline(ss, pkg, ',');
        std::getline(ss, dnp_str, ',');

        bool dnp = (!dnp_str.empty() && (trim(dnp_str) == "1" || to_upper(trim(dnp_str)) == "DNP"));

        std::stringstream des_ss(des_field);
        std::string single_des;
        while (des_ss >> single_des) {
            single_des = trim(single_des);
            if (!single_des.empty()) {
                bom_map[to_upper(single_des)] = {trim(mpn), dnp, false};
            }
        }
    }

    // Зчитування CPL (Pick and Place)
    std::ifstream cpl_stream(cpl_file);
    if (!cpl_stream.is_open()) {
        std::cerr << "Помилка: не вдалося відкрити CPL файл: " << cpl_file << "\n";
        return 2;
    }

    is_first = true;
    while (std::getline(cpl_stream, line)) {
        if (line.empty() || is_first) {
            is_first = false;
            continue;
        }
        std::stringstream ss(line);
        std::string des, xs, ys, rots, layer;
        if (!std::getline(ss, des, ',')) continue;
        std::getline(ss, xs, ',');
        std::getline(ss, ys, ',');
        std::getline(ss, rots, ',');
        std::getline(ss, layer, ',');

        std::string key = to_upper(trim(des));
        if (!key.empty()) {
            double x = xs.empty() ? 0.0 : std::stod(xs);
            double y = ys.empty() ? 0.0 : std::stod(ys);
            double rot = rots.empty() ? 0.0 : std::stod(rots);
            cpl_map[key] = {x, y, rot, trim(layer), false};
        }
    }

    std::cout << "=== ВАЛІДАЦІЯ ВИРОБНИЧОГО ПАКЕТА: BOM vs CPL ===\n";
    std::cout << "Унікальних референсів: BOM=" << bom_map.size() 
              << ", CPL=" << cpl_map.size() << "\n\n";

    int errors = 0;
    int warnings = 0;

    // Перевірка 1: кожен елемент BOM має бути в CPL (якщо не DNP)
    for (auto& [des, bom_val] : bom_map) {
        auto it = cpl_map.find(des);
        if (it != cpl_map.end()) {
            bom_val.found_in_cpl = true;
            it->second.found_in_bom = true;
            if (bom_val.is_dnp) {
                std::cout << "[УВАГА / DNP] " << des << " є в CPL (X=" << it->second.x 
                          << ", Y=" << it->second.y << "), але в BOM стоїть прапорець DNP!\n";
                warnings++;
            }
        } else if (!bom_val.is_dnp) {
            std::cout << "[ПОМИЛКА] " << des << " (" << bom_val.mpn 
                      << ") зазначено в BOM, але немає у файлі Pick-and-Place!\n";
            errors++;
        }
    }

    // Перевірка 2: кожен елемент CPL повинен бути у відомості BOM
    for (const auto& [des, cpl_val] : cpl_map) {
        if (!cpl_val.found_in_bom) {
            std::cout << "[ПОМИЛКА] " << des << " розміщено на платі (X=" << cpl_val.x 
                      << ", Y=" << cpl_val.y << "), але повністю відсутній у списку BOM!\n";
            errors++;
        }
    }

    std::cout << "\nПідсумок перевірки: критичних помилок=" << errors 
              << ", зауважень=" << warnings << "\n";

    if (errors > 0) {
        std::cout << "РЕЗУЛЬТАТ: ВІДХИЛЕНО. Необхідно синхронізувати експорт із САПР.\n";
        return 1;
    }

    std::cout << "РЕЗУЛЬТАТ: СХВАЛЕНО. Файли готові до відправлення на виробництво.\n";
    return 0;
}
