#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_set>
#include <format>

namespace eda {

enum class EcoStatus {
    NoChange,
    NetCreated,
    NetDeleted,
    PinsModified
};

struct EcoDiffResult {
    std::string net_name;
    EcoStatus status{EcoStatus::NoChange};
    std::size_t added_pins_count{0};
    std::size_t removed_pins_count{0};
};

class EcoEngine {
public:
    static EcoDiffResult compute_diff(std::string_view net_name,
                                      const std::vector<std::string>& old_pins,
                                      const std::vector<std::string>& new_pins) {
        EcoDiffResult result{std::string(net_name)};

        if (old_pins.empty() && !new_pins.empty()) {
            result.status = EcoStatus::NetCreated;
            result.added_pins_count = new_pins.size();
            return result;
        }
        if (!old_pins.empty() && new_pins.empty()) {
            result.status = EcoStatus::NetDeleted;
            result.removed_pins_count = old_pins.size();
            return result;
        }

        std::unordered_set<std::string_view> old_set(old_pins.begin(), old_pins.end());
        std::unordered_set<std::string_view> new_set(new_pins.begin(), new_pins.end());

        for (const auto& pin : new_pins) {
            if (!old_set.contains(pin)) {
                result.added_pins_count++;
            }
        }
        for (const auto& pin : old_pins) {
            if (!new_set.contains(pin)) {
                result.removed_pins_count++;
            }
        }

        if (result.added_pins_count == 0 && result.removed_pins_count == 0) {
            result.status = EcoStatus::NoChange;
        } else {
            result.status = EcoStatus::PinsModified;
        }
        return result;
    }
};

} // namespace eda
