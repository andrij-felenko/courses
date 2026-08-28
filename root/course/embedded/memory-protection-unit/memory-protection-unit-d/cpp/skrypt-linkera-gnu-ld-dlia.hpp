#include <cstdint>
#include <span>

// Експорт меж секцій із скрипту компонувальника
extern "C" {
    extern const uint32_t _stext;
    extern const uint32_t _etext;
    extern const uint32_t _skernel_data;
    extern const uint32_t _ekernel_data;
    extern const uint32_t _stask_stacks;
    extern const uint32_t _etask_stacks;
}

namespace MemoryLayout {
    inline std::span<const uint8_t> flash_code_region() noexcept {
        auto start = reinterpret_cast<const uint8_t*>(&_stext);
        auto end   = reinterpret_cast<const uint8_t*>(&_etext);
        return {start, static_cast<std::size_t>(end - start)};
    }

    inline std::span<uint8_t> kernel_data_region() noexcept {
        auto start = reinterpret_cast<uint8_t*>(const_cast<uint32_t*>(&_skernel_data));
        auto end   = reinterpret_cast<uint8_t*>(const_cast<uint32_t*>(&_ekernel_data));
        return {start, static_cast<std::size_t>(end - start)};
    }
}
