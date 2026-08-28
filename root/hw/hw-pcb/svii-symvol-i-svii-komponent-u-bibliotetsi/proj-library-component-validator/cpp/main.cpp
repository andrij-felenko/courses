#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <cctype>

enum class PinType {
    Input,
    Output,
    Bidirectional,
    TriState,
    Passive,
    PowerIn,
    PowerOut,
    OpenDrain,
    NotConnected
};

std::string_view to_string(PinType t) noexcept {
    switch (t) {
        case PinType::Input:         return "Input";
        case PinType::Output:        return "Output";
        case PinType::Bidirectional: return "Bidirectional";
        case PinType::TriState:      return "Tri-state";
        case PinType::Passive:       return "Passive";
        case PinType::PowerIn:       return "Power In";
        case PinType::PowerOut:      return "Power Out";
        case PinType::OpenDrain:     return "Open Drain";
        case PinType::NotConnected:  return "Not Connected";
    }
    return "Unknown";
}

struct SymbolPin {
    std::string number;
    std::string name;
    std::string unit{"A"};
    PinType type{PinType::Passive};
    bool is_active_low{false};
};

struct FootprintPad {
    std::string number;
    std::string name;
    bool is_mechanical{false};
};

struct AuditReport {
    std::vector<std::string> errors;
    std::vector<std::string> warnings;

    [[nodiscard]] bool passed() const noexcept {
        return errors.empty();
    }
};

class ComponentValidator {
public:
    std::string mpn;
    std::string manufacturer;
    std::string footprint_ref;
    std::string datasheet_url;

    std::vector<SymbolPin> pins;
    std::vector<FootprintPad> pads;
    std::unordered_map<std::string, std::string> pin_to_pad_map;

    [[nodiscard]] AuditReport execute_audit() const {
        AuditReport report;

        // 1. Аудит атрибутів BOM
        if (mpn.empty()) {
            report.errors.push_back("Порожній номер деталі виробника (MPN)!");
        }
        if (manufacturer.empty()) {
            report.errors.push_back("Відсутня назва компанії-виробника!");
        }
        if (footprint_ref.empty()) {
            report.errors.push_back("Не задано посилання на посадкове місце (Footprint)!");
        }
        if (datasheet_url.empty() || !datasheet_url.starts_with("http")) {
            report.warnings.push_back("Посилання на Datasheet відсутнє або не є коректним HTTP URL.");
        }

        // 2. Аудит пінів символу
        if (pins.empty()) {
            report.errors.push_back("Символ компонента не містить жодного виводу.");
        }

        std::unordered_set<std::string> scoped_pins;
        for (const auto& pin : pins) {
            std::string scope_key = pin.unit + ":" + pin.number;
            if (!scoped_pins.insert(scope_key).second) {
                report.errors.push_back("Дублювання номера виводу '" + pin.number + 
                                       "' у функційній секції Unit " + pin.unit);
            }

            if (pin.is_active_low) {
                bool has_prefix = pin.name.starts_with('~') || pin.name.starts_with('n') || pin.name.starts_with('/');
                bool has_suffix = pin.name.ends_with('#') || pin.name.ends_with("_N");
                if (!has_prefix && !has_suffix) {
                    report.warnings.push_back("Пін " + pin.number + " (" + pin.name + 
                                             ") позначений Active-Low без стандартного індикатора інверсії.");
                }
            }
        }

        // 3. Аудит площадок посадкового місця та правил JEDEC
        if (pads.empty()) {
            report.errors.push_back("Посадкове місце не містить контактних площадок.");
        }

        const std::string_view forbidden_bga = "IOQSXZ";
        std::unordered_set<std::string> unique_pads;

        for (const auto& pad : pads) {
            if (!unique_pads.insert(pad.number).second) {
                report.errors.push_back("Посадкове місце містить дубльовану площадку '" + pad.number + "'!");
            }

            for (char ch : pad.number) {
                char upper_ch = static_cast<char>(std::toupper(static_cast<unsigned char>(ch)));
                if (std::isalpha(static_cast<unsigned char>(ch)) && forbidden_bga.find(upper_ch) != std::string_view::npos) {
                    report.errors.push_back("Площадка BGA '" + pad.number + 
                                           "' містить заборонену стандартом JEDEC літеру '" + 
                                           std::string(1, upper_ch) + "'");
                }
            }
        }

        // 4. Аудит бієкції Pin-to-Pad
        std::unordered_set<std::string> mapped_pads;

        for (const auto& pin : pins) {
            if (pin.type == PinType::NotConnected) {
                continue;
            }

            auto it = pin_to_pad_map.find(pin.number);
            if (it == pin_to_pad_map.end()) {
                report.errors.push_back("Пін " + pin.number + " (" + pin.name + ", тип " + 
                                       std::string(to_string(pin.type)) + ") не має прив'язки до площадки.");
            } else {
                const std::string& target_pad = it->second;
                auto pad_it = std::find_if(pads.begin(), pads.end(), [&](const FootprintPad& p) {
                    return p.number == target_pad;
                });

                if (pad_it == pads.end()) {
                    report.errors.push_back("Пін " + pin.number + " змаплений на неіснуючу контактну площадку '" + 
                                           target_pad + "'!");
                } else {
                    mapped_pads.insert(target_pad);
                }
            }
        }

        // 5. Пошук незмапленої міді
        for (const auto& pad : pads) {
            if (!pad.is_mechanical && !mapped_pads.contains(pad.number)) {
                report.warnings.push_back("Контактна площадка '" + pad.number + 
                                         "' (" + pad.name + ") на платі не зв'язана з жодним піном схеми.");
            }
        }

        return report;
    }
};

int main() {
    ComponentValidator mcu;
    mcu.mpn = "STM32F401RET6";
    mcu.manufacturer = "STMicroelectronics";
    mcu.footprint_ref = "Package_QFP:LQFP-64_10x10mm_P0.5mm";
    mcu.datasheet_url = "https://www.st.com/resource/en/datasheet/stm32f401re.pdf";

    mcu.pins = {
        {"1", "VBAT", "A", PinType::PowerIn, false},
        {"2", "PC13", "A", PinType::Bidirectional, false},
        {"7", "~{NRST}", "A", PinType::Input, true}
    };

    mcu.pads = {
        {"1", "Pad_1", false},
        {"2", "Pad_2", false},
        {"7", "Pad_7", false}
    };

    mcu.pin_to_pad_map = {
        {"1", "1"},
        {"2", "2"},
        {"7", "7"}
    };

    auto report = mcu.execute_audit();

    std::cout << "=====================================================\n";
    std::cout << "РЕЗУЛЬТАТ АУДИТУ КОМПОНЕНТА: " << mcu.mpn << "\n";
    std::cout << "=====================================================\n";

    for (const auto& err : report.errors) {
        std::cout << "[ПОМИЛКА] " << err << "\n";
    }
    for (const auto& warn : report.warnings) {
        std::cout << "[ПОПЕРЕДЖЕННЯ] " << warn << "\n";
    }

    if (report.passed()) {
        std::cout << "[СХВАЛЕНО] Усі перевірки пройдено успішно.\n";
        return 0;
    }

    std::cout << "[ВІДХИЛЕНО] Знайдено дефекти! Імпорт у бібліотеку заборонено.\n";
    return 1;
}
