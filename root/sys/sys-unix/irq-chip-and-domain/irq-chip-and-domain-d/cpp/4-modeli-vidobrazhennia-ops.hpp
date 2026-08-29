#pragma once
#include <cstdint>
#include "4-modeli-vidobrazhennia.hpp"

namespace kernel::irq {
struct IrqDomainOps {
    int (*map)(IrqDomain* d, unsigned int virq, uint32_t hwirq){nullptr};
    void (*unmap)(IrqDomain* d, unsigned int virq){nullptr};
    int (*xlate)(IrqDomain* d, const uint32_t* spec, unsigned int size, uint32_t* out_hw, unsigned int* out_type){nullptr};
};
}
