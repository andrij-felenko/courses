#include <iostream>
#include <vector>
#include <optional>
#include <string_view>
#include <cstdint>
#include <format>

struct Packet {
    uint16_t src;
    uint16_t dst;
    uint8_t  ttl{8};
    uint8_t  hopCount{0};
    std::string_view payload;
};

/* Базовий інтерфейс вузла маршрутизації */
class RoutingNode {
public:
    explicit RoutingNode(uint16_t address) : address_{address} {}
    virtual ~RoutingNode() = default;

    [[nodiscard]] uint16_t address() const noexcept { return address_; }
    [[nodiscard]] virtual std::optional<uint16_t> forward(const Packet& pkt) const = 0;

protected:
    uint16_t address_;
};

/* --- 1. Реалізація Зірки (Star) --- */
class StarNode final : public RoutingNode {
public:
    StarNode(uint16_t address, uint16_t hubAddress)
        : RoutingNode(address), hubAddress_{hubAddress} {}

    [[nodiscard]] std::optional<uint16_t> forward(const Packet& pkt) const noexcept override {
        if (pkt.dst == address_) {
            return address_;
        }
        if (address_ == hubAddress_) {
            return pkt.dst; /* Шлюз має прямі радіолінки до всіх пристроїв */
        }
        return hubAddress_; /* Клієнтський вузол шле все на шлюз */
    }

private:
    uint16_t hubAddress_;
};

/* --- 2. Реалізація Кластерного Дерева (Cskip / Hierarchical Tree) --- */
class TreeNode final : public RoutingNode {
public:
    TreeNode(uint16_t address, uint16_t parentAddress, uint16_t subMin, uint16_t subMax)
        : RoutingNode(address), parent_{parentAddress}, subMin_{subMin}, subMax_{subMax} {}

    void addChildRouter(uint16_t childAddr) {
        childRouters_.push_back(childAddr);
    }

    [[nodiscard]] std::optional<uint16_t> forward(const Packet& pkt) const noexcept override {
        if (pkt.dst == address_) {
            return address_;
        }

        /* Перевіряємо попадання в префікс піддерева */
        if (pkt.dst >= subMin_ && pkt.dst <= subMax_) {
            for (uint16_t child : childRouters_) {
                if (pkt.dst == child || (pkt.dst > child && pkt.dst < child + 0x0100)) {
                    return child;
                }
            }
            return pkt.dst; /* Прямий листок */
        }

        /* Ціль поза піддеревом — маршрутизація вгору до кореня */
        return parent_;
    }

private:
    uint16_t parent_;
    uint16_t subMin_;
    uint16_t subMax_;
    std::vector<uint16_t> childRouters_;
};

/* --- 3. Реалізація Чарунки з динамічним відновленням (Mesh) --- */
struct Neighbor {
    uint16_t address;
    uint16_t linkCost; /* Оцінка якості (ETX) */
    bool     isAlive;
};

struct RouteEntry {
    uint16_t destination;
    uint16_t primaryNextHop;
    uint16_t backupNextHop;
};

class MeshNode final : public RoutingNode {
public:
    explicit MeshNode(uint16_t address) : RoutingNode(address) {}

    void addNeighbor(Neighbor n) { neighbors_.push_back(n); }
    void addRoute(RouteEntry r)  { routes_.push_back(r); }

    void setLinkStatus(uint16_t neighborAddr, bool alive) {
        for (auto& n : neighbors_) {
            if (n.address == neighborAddr) {
                n.isAlive = alive;
                break;
            }
        }
    }

    [[nodiscard]] std::optional<uint16_t> forward(const Packet& pkt) const noexcept override {
        if (pkt.dst == address_) {
            return address_;
        }

        for (const auto& route : routes_) {
            if (route.destination == pkt.dst) {
                /* Перевірка працездатності первинного шляху */
                if (isNeighborAlive(route.primaryNextHop)) {
                    return route.primaryNextHop;
                }
                /* Локальне відновлення на резервний шлях */
                if (isNeighborAlive(route.backupNextHop)) {
                    return route.backupNextHop;
                }
            }
        }
        return std::nullopt; /* Маршрут недоступний */
    }

private:
    [[nodiscard]] bool isNeighborAlive(uint16_t neighborAddr) const noexcept {
        for (const auto& n : neighbors_) {
            if (n.address == neighborAddr) {
                return n.isAlive;
            }
        }
        return false;
    }

    std::vector<Neighbor>   neighbors_;
    std::vector<RouteEntry> routes_;
};

int main() {
    std::cout << "=== C++ Routing Engine Simulation ===\n\n";

    const Packet samplePkt{
        .src = 0x0005,
        .dst = 0x0001,
        .ttl = 8,
        .hopCount = 0,
        .payload = "SensorData: 42.0"
    };

    /* 1. Star */
    const StarNode starNode(0x0005, 0x0001);
    if (auto nextHop = starNode.forward(samplePkt)) {
        std::cout << std::format("[Star] Forwarding from 0x{:04X} to Hub -> 0x{:04X}\n",
                                 starNode.address(), *nextHop);
    }

    /* 2. Tree */
    TreeNode treeNode(0x0010, 0x0000, 0x0010, 0x00FF);
    treeNode.addChildRouter(0x0020);
    const Packet outOfSubtreePkt{ .src = 0x0015, .dst = 0x0500, .payload = "Upward" };
    if (auto nextHop = treeNode.forward(outOfSubtreePkt)) {
        std::cout << std::format("[Tree] Target 0x{:04X} out of subtree. Forwarding UP -> 0x{:04X}\n",
                                 outOfSubtreePkt.dst, *nextHop);
    }

    /* 3. Mesh Failover */
    MeshNode meshNode(0x0003);
    meshNode.addNeighbor({ .address = 0x0002, .linkCost = 10, .isAlive = false });
    meshNode.addNeighbor({ .address = 0x0004, .linkCost = 22, .isAlive = true });
    meshNode.addRoute({ .destination = 0x0001, .primaryNextHop = 0x0002, .backupNextHop = 0x0004 });

    if (auto nextHop = meshNode.forward(samplePkt)) {
        std::cout << std::format("[Mesh] Primary next-hop 0x0002 dead. Local repair -> 0x{:04X}\n",
                                 *nextHop);
    }

    return 0;
}
