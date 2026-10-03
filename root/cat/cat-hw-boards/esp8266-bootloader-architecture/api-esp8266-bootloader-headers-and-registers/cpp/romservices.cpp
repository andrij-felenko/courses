#include <cstdint>
#include <cstddef>

class RomServices {
public:
    using PrintfType  = int (*)(const char*, ...);
    using SpiReadType = int (*)(std::uint32_t, std::uint32_t*, std::uint32_t);

    static constexpr std::uintptr_t EtsPrintfAddress = 0x40002478U;
    static constexpr std::uintptr_t SpiReadAddress   = 0x40004b20U;

    static void printStartupBanner(const char* bannerText) noexcept {
        auto romPrintf = reinterpret_cast<PrintfType>(EtsPrintfAddress);
        romPrintf("[ROM-LOG] %s\n", bannerText);
    }

    static bool readHeader(std::uint32_t offset, std::uint32_t* buffer, std::uint32_t bytes) noexcept {
        auto romSpiRead = reinterpret_cast<SpiReadType>(SpiReadAddress);
        return romSpiRead(offset, buffer, bytes) == 0;
    }
};
