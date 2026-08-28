#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <optional>

namespace eda {

struct PinNode {
    std::string refdes;
    std::string pin_number;
    std::string pin_type;
};

struct NetEntry {
    std::string name;
    int code{0};
    std::vector<PinNode> pins;
};

class NetlistGraph {
public:
    bool add_pin(std::string_view net_name, std::string_view refdes,
                 std::string_view pin, std::string_view pintype = "passive") {
        auto& net = nets_[std::string(net_name)];
        if (net.name.empty()) {
            net.name = std::string(net_name);
            net.code = static_cast<int>(nets_.size());
        }
        net.pins.push_back(PinNode{std::string(refdes), std::string(pin), std::string(pintype)});
        return true;
    }

    [[nodiscard]] std::optional<std::reference_wrapper<const NetEntry>>
    find_net(std::string_view net_name) const noexcept {
        auto it = nets_.find(std::string(net_name));
        if (it != nets_.end()) {
            return std::cref(it->second);
        }
        return std::nullopt;
    }

    [[nodiscard]] const std::unordered_map<std::string, NetEntry>& all_nets() const noexcept {
        return nets_;
    }

    [[nodiscard]] std::size_t total_nets() const noexcept {
        return nets_.size();
    }

private:
    std::unordered_map<std::string, NetEntry> nets_;
};

} // namespace eda
