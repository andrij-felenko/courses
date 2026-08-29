#pragma once
#include <cstdint>
#include <string>

namespace kernel::irq {
struct IrqData {
    uint32_t irq{p};
    uint32_t hwirq{0};
    void* chip_data{nullptr};
};
struct IrqChip {
    std::string name;
    void (*irq_mask)(IrqData* data){nullptr};
    void (*irq_unmask)(IrqData* data){nullptr};
    void (*irq_ack)(IrqData* data){nullptr};
    void (*irq_eoi)(IrqData* data){nullptr};
    int (*irq_set_type)(IrqData* data, unsigned int type){nullptr};
    unsigned long flags{0};
};
}
