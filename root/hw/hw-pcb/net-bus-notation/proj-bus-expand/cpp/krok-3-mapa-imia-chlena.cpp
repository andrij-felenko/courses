#include <map>

struct Pin { std::string part; int pad; };   // напр. {"U3", 12}

// Ланцюг = ім'я + усі піни, що мусять стати однією міддю.
// Мапа ім'я→піни — це РЕАЛЬНИЙ опис плати; вектор у ній уже не фігурує.
using Netlist = std::map<std::string, std::vector<Pin>>;

// Завести шину у нетлист: розгорнути й приписати кожному членові його пін.
// pins — піни приймача в ТОМУ Ж порядку, що й члени шини.
static void attach_bus(Netlist& net, const BusName& bn,
                       const std::vector<Pin>& pins) {
    std::vector<std::string> members = expand(bn);
    for (size_t i = 0; i < members.size() && i < pins.size(); ++i)
        net[members[i]].push_back(pins[i]);   // D3 → {U3.pad}, D2 → {…}, …
}
