#include <iostream>
#include <vector>
#include <array>
#include <optional>
#include <algorithm>
#include <cstdint>

namespace dist {

inline constexpr size_t NodeCount = 3;

enum class ConsistencyMode {
    Linearizable,
    Causal,
    Eventual
};

struct VectorClock {
    std::array<uint32_t, NodeCount> clock{};

    [[nodiscard]] bool isCausallyReady(const VectorClock& nodeVc, size_t origin) const noexcept {
        if (clock[origin] != nodeVc.clock[origin] + 1) {
            return false;
        }
        for (size_t i = 0; i < NodeCount; ++i) {
            if (i != origin && clock[i] > nodeVc.clock[i]) {
                return false;
            }
        }
        return true;
    }
};

struct RegisterEntry {
    int value{0};
    uint64_timestamp{0};
    VectorClock vc{};
    size_t originNode{0};
};

class ClusterSimulator {
public:
    explicit ClusterSimulator(ConsistencyMode mode) noexcept
        : mode_{mode} {}

    void write(size_t targetNode, int value) {
        timer_ += 10;
        auto& node = nodes_[targetNode];
        node.current.value = value;
        node.current.timestamp = timer_;
        node.current.originNode = targetNode;
        node.current.vc.clock[targetNode]++;

        std::cout << "[WRITE] Вузол " << targetNode << ": value=" << value
                  << " (VC: [" << node.current.vc.clock[0] << ", "
                  << node.current.vc.clock[1] << ", "
                  << node.current.vc.clock[2] << "], t=" << timer_ << ")\n";

        if (mode_ == ConsistencyMode::Linearizable) {
            for (auto& n : nodes_) {
                n.current = node.current;
            }
            std::cout << "  -> [Кворум W=3] Синхронно зафіксовано на всіх вузлах.\n";
        }
    }

    void deliverReplication(size_t toNode, const RegisterEntry& entry) {
        auto& dest = nodes_[toNode];

        if (mode_ == ConsistencyMode::Eventual) {
            if (entry.timestamp >= dest.current.timestamp) {
                dest.current = entry;
                std::cout << "[EVENTUAL DELIVER] Вузол " << toNode
                          << " застосував value=" << entry.value << '\n';
            }
            return;
        }

        if (mode_ == ConsistencyMode::Causal) {
            if (entry.vc.isCausallyReady(dest.current.vc, entry.originNode)) {
                applyEntry(toNode, entry);
                drainBuffer(toNode);
            } else {
                dest.buffer.push_back(entry);
                std::cout << "[CAUSAL BUFFER] Вузол " << toNode
                          << " відклав value=" << entry.value << " (очікує залежності)\n";
            }
        }
    }

    [[nodiscard]] int read(size_t targetNode) const noexcept {
        const auto& node = nodes_[targetNode];
        std::cout << "[READ] Вузол " << targetNode << " -> value=" << node.current.value
                  << " (VC: [" << node.current.vc.clock[0] << ", "
                  << node.current.vc.clock[1] << ", "
                  << node.current.vc.clock[2] << "])\n";
        return node.current.value;
    }

    [[nodiscard]] const RegisterEntry& getEntry(size_t nodeIndex) const noexcept {
        return nodes_[nodeIndex].current;
    }

private:
    struct NodeState {
        RegisterEntry current{};
        std::vector<RegisterEntry> buffer{};
    };

    void applyEntry(size_t nodeId, const RegisterEntry& entry) {
        auto& node = nodes_[nodeId];
        node.current.value = entry.value;
        node.current.timestamp = entry.timestamp;
        node.current.vc.clock[entry.originNode] = entry.vc.clock[entry.originNode];
        std::cout << "[CAUSAL DELIVER] Вузол " << nodeId << " застосував value=" << entry.value
                  << " (Новий VC: [" << node.current.vc.clock[0] << ", "
                  << node.current.vc.clock[1] << ", "
                  << node.current.vc.clock[2] << "])\n";
    }

    void drainBuffer(size_t nodeId) {
        auto& dest = nodes_[nodeId];
        bool progressed = true;
        while (progressed) {
            progressed = false;
            for (auto it = dest.buffer.begin(); it != dest.buffer.end(); ++it) {
                if (it->vc.isCausallyReady(dest.current.vc, it->originNode)) {
                    RegisterEntry readyEntry = *it;
                    dest.buffer.erase(it);
                    std::cout << "  -> [CAUSAL UNBUFFER] Вузол " << nodeId
                              << " розблокував value=" << readyEntry.value << '\n';
                    applyEntry(nodeId, readyEntry);
                    progressed = true;
                    break;
                }
            }
        }
    }

    ConsistencyMode mode_;
    uint64_t timer_{100};
    std::array<NodeState, NodeCount> nodes_{};
};

} // namespace dist

int main() {
    using namespace dist;
    std::cout << "=== 1. ТЕСТ ПРИЧИННОЇ КОНСИСТЕНТНОСТІ (C++20) ===\n";
    ClusterSimulator sim{ConsistencyMode::Causal};

    sim.write(0, 10);
    RegisterEntry postAlice = sim.getEntry(0);

    sim.deliverReplication(1, postAlice);
    sim.write(1, 20);
    RegisterEntry replyBob = sim.getEntry(1);

    std::cout << "\n--- Мережевий збій: відповідь Боба прибула на Вузол 2 раніше за пост Аліси ---\n";
    sim.deliverReplication(2, replyBob);
    sim.read(2);

    std::cout << "\n--- Пост Аліси нарешті дійшов до Вузла 2 ---\n";
    sim.deliverReplication(2, postAlice);
    sim.read(2);

    return 0;
}
