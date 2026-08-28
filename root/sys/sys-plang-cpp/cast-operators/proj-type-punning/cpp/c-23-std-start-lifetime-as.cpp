#include <memory>
#include <cstddef>
#include <span>

struct DmaDescriptor {
    uint64_t buffer_address;
    uint32_t length;
    uint32_t status_flags;
};

// C++23: Початок часу життя об'єкта в існуючому сирому буфері БЕЗ копіювання
const DmaDescriptor* access_dma_buffer(const void* raw_dma_memory) noexcept {
    // Явно інформує компілятор про створення об'єкта типу DmaDescriptor за цією адресою.
    // Запобігає UB та дозволяє оптимізатору будувати коректні ланцюги аліасингу.
    return std::start_lifetime_as<const DmaDescriptor>(raw_dma_memory);
}
