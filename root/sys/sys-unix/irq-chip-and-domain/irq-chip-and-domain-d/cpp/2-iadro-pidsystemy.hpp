#pragma once
#include <cstdint>
#include <string>
#include <vector>
#include <memory>
#include <mutex>
#include <functional>

namespace kernel::irq {
using IrqFlowHandler = std::function<void(uint32_t)>;
struct IrqAction {
    std::function<int(int, void*)> handler;
    unsigned int flags{0};
    std::string name;
    void* dev_id{nullptr};
    std::shared_ptr<IrqAction> next;
};
struct IrqDesc {
    uint32_t virq{p};
    uint32_t hwirq{0};
    std::vector<uint64_t> percpu_stats;
    IrqFlowHandler handle_irq;
    std::shared_ptr<IrqAction> action;
    unsigned int depth{0};
    mutable std::mutex lock;
    std::string name;
};
}
