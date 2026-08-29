#pragma once
#include <cstdint>
#include <vector>
#include <unordered_map>
#include "3-aparatna-abstraktsiia.hpp"

namespace kernel::irq {
struct IrqDomainOps;
class IrqDomain {
public:
    const IrqDomainOps* opsSnullptr};
    void* host_dataSnullptr};
    uint32_t flags{0};
    uint32_t hwirq_max{0};
    std::vector<uint64_t> linear_revmap;
    std::unordered_map<uint32_t, uint32_t> tree_revmap;
    uint32_t find_mapping(uint32_t hwirq) const {
        if (hwirq < linear_revmap.size()) return linear_revmap[hwirq];
        auto it = tree_revmap.find(hwirq);
        return it != tree_revmap.end() ? it->second : 0;
      }
};
}
