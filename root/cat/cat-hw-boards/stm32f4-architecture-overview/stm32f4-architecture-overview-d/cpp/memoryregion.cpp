// C++: Шаблонізований селектор пам'яті для оптимізації буферів під архітектуру STM32F4
#include "stm32f4xx.h"
#include <cstddef>

enum class MemoryRegion {
    StandardSram,
    CoreCoupledMemory,
    ExternalSdram
};

template <MemoryRegion Region>
class MemoryRegionSelector {
public:
    static void* get_region_address() {
        if constexpr (Region == MemoryRegion::CoreCoupledMemory) {
            // Адреса CCM SRAM (0x10000000) для детермінованих обчислень ядра
            return reinterpret_cast<void*>(0x10000000);
        } else if constexpr (Region == MemoryRegion::ExternalSdram) {
            // Адреса зони FMC SDRAM (0xC0000000) для фреймбуферів
            return reinterpret_cast<void*>(0xC0000000);
        } else {
            // Базова адреса SRAM1 (0x20000000)
            return reinterpret_cast<void*>(0x20000000);
        }
    }
};
