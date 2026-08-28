#include <cstddef>
#include <new>

class HardwareDMAController {
public:
    [[nodiscard]] void* allocate_coherent_buffer(std::size_t size) {
        // Локально документуємо виняток для виділення сирої DMA пам'яті
        [[gsl::suppress("cppcoreguidelines-owning-memory", 
          justification = "DMA-буфер вирівнюється за сторінкою пам'яті; звільняється в ~HardwareDMAController")]]
        void* dma_buffer = ::operator new(size, std::align_val_t{4096});
        return dma_buffer;
    }
};
