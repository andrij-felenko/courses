#include <iostream>
#include <vector>
#include <memory>
#include <chrono>
#include <cstdint>
#include <limits>

constexpr std::uint32_t NODE_COUNT = 10'000'000;

/* 1. Класичний вузол з 64-бітним покажчиком (16 байтів через вирівнювання) */
struct RawNode {
    std::uint32_t value{0};
    RawNode* next{nullptr};
};

/* Строго типізований дескриптор індексу для унеможливлення плутанини чисел та адрес */
enum class NodeId : std::uint32_t {
    Invalid = std::numeric_limits<std::uint32_t>::max()
};

/* 2. Компактний вузол з 32-бітним індексом арени (8 байтів) */
struct CompactNode {
    std::uint32_t value{0};
    NodeId next_id{NodeId::Invalid};
};

/* RAII-контейнер для арени вузлів */
class NodeArena {
public:
    explicit NodeArena(std::size_t capacity) {
        m_storage.reserve(capacity);
    }

    NodeId allocate(std::uint32_t value, NodeId next = NodeId::Invalid) {
        auto idx = static_cast<NodeId>(m_storage.size());
        m_storage.push_back(CompactNode{value, next});
        return idx;
    }

    [[nodiscard]] const CompactNode& get(NodeId id) const noexcept {
        return m_storage[static_cast<std::uint32_t>(id)];
    }

    [[nodiscard]] std::size_t byte_size() const noexcept {
        return m_storage.size() * sizeof(CompactNode);
    }

private:
    std::vector<CompactNode> m_storage;
};

/* Послідовний обхід сирого списку */
[[nodiscard]] std::uint64_t traverse_raw(const RawNode* head) noexcept {
    std::uint64_t sum = 0;
    const RawNode* curr = head;
    while (curr != nullptr) {
        sum += curr->value;
        curr = curr->next;
    }
    return sum;
}

/* Послідовний обхід компактного індексного списку */
[[nodiscard]] std::uint64_t traverse_compact(const NodeArena& arena, NodeId head_id) noexcept {
    std::uint64_t sum = 0;
    NodeId curr = head_id;
    while (curr != NodeId::Invalid) {
        const auto& node = arena.get(curr);
        sum += node.value;
        curr = node.next_id;
    }
    return sum;
}

int main() {
    std::cout << "Розмір RawNode: " << sizeof(RawNode) << " байтів\n";
    std::cout << "Розмір CompactNode: " << sizeof(CompactNode) << " байтів\n\n";

    // Побудова списку на сирих покажчиках
    std::vector<RawNode> raw_storage(NODE_COUNT);
    for (std::uint32_t i = 0; i < NODE_COUNT; ++i) {
        raw_storage[i].value = i;
        raw_storage[i].next = (i + 1 < NODE_COUNT) ? &raw_storage[i + 1] : nullptr;
    }

    // Побудова компактної арени
    NodeArena arena(NODE_COUNT);
    for (std::uint32_t i = 0; i < NODE_COUNT; ++i) {
        arena.allocate(i, (i + 1 < NODE_COUNT) ? static_cast<NodeId>(i + 1) : NodeId::Invalid);
    }

    // Замір швидкості обходу RawNode
    auto t0 = std::chrono::high_resolution_clock::now();
    auto sum_raw = traverse_raw(&raw_storage[0]);
    auto t1 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> dur_raw = t1 - t0;

    // Замір швидкості обходу CompactNode
    auto t2 = std::chrono::high_resolution_clock::now();
    auto sum_compact = traverse_compact(arena, static_cast<NodeId>(0));
    auto t3 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> dur_compact = t3 - t2;

    std::cout << "Raw Node:     сума = " << sum_raw
              << ", час = " << dur_raw.count() << " с ("
              << (NODE_COUNT * sizeof(RawNode)) / (1024.0 * 1024.0) << " МБ)\n";

    std::cout << "Compact Node: сума = " << sum_compact
              << ", час = " << dur_compact.count() << " с ("
              << arena.byte_size() / (1024.0 * 1024.0) << " МБ)\n";

    return 0;
}
