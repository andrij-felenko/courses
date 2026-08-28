#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <optional>
#include <string_view>

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

struct SymbolPin {
    int logical_number;
    std::string name;
    PinType type;
    bool is_active_low{false};
};

struct FootprintPad {
    int pad_number;
    std::string physical_name;
};

class AtomicComponent {
public:
    std::string mpn;
    std::string manufacturer;
    std::string footprint_name;
    std::string datasheet_url;
    
    std::vector<SymbolPin> pins;
    std::vector<FootprintPad> pads;
    std::unordered_map<int, int> pin_to_pad_map; // pin_number -> pad_number

    [[nodiscard]] std::optional<std::string> validate() const {
        if (mpn.empty() || manufacturer.empty()) {
            return "Критичний дефект BOM: порожній MPN або виробник.";
        }
        if (pins.empty() || pads.empty()) {
            return "Геометричний дефект: відсутні піни символу або площадки посадкового місця.";
        }

        std::unordered_set<int> unique_pins;
        for (const auto& pin : pins) {
            if (!unique_pins.insert(pin.logical_number).second) {
                return "Дублювання номера піна символу: " + std::to_string(pin.logical_number);
            }
        }

        std::unordered_set<int> target_pads;
        for (const auto& pin : pins) {
            auto it = pin_to_pad_map.find(pin.logical_number);
            if (it == pin_to_pad_map.end()) {
                if (pin.type != PinType::NotConnected) {
                    return "Незмаплений пін символу: " + std::to_string(pin.logical_number) + " (" + pin.name + ")";
                }
            } else {
                int target_pad = it->second;
                bool pad_exists = false;
                for (const auto& pad : pads) {
                    if (pad.pad_number == target_pad) {
                        pad_exists = true;
                        break;
                    }
                }
                if (!pad_exists) {
                    return "Пін " + std::to_string(pin.logical_number) + " вказує на неіснуючу площадку " + std::to_string(target_pad);
                }
                target_pads.insert(target_pad);
            }
        }

        return std::nullopt; // Успішна валідація
    }
};
