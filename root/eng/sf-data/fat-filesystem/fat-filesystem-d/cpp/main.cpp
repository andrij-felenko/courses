#include <cstdint>
#include <iostream>
#include <span>
#include <optional>

namespace fat32 {

#pragma pack(push, 1)
struct alignas(1) BootRecord {
    uint8_t  jmpBoot[3];
    char     oemName[8];
    uint16_t bytesPerSec;
    uint8_t  secPerClus;
    uint16_t rsvdSecCnt;
    uint8_t  numFATs;
    uint16_t rootEntCnt;
    uint16_t totSec16;
    uint8_t  media;
    uint16_t fatSz16;
    uint16_t secPerTrk;
    uint16_t numHeads;
    uint32_t hiddSec;
    uint32_t totSec32;
    uint32_t fatSz32;
    uint16_t extFlags;
    uint16_t fsVer;
    uint32_t rootClus;
    uint16_t fsInfo;
    uint16_t bkBootSec;
    uint8_t  reserved[12];
    uint8_t  drvNum;
    uint8_t  reserved1;
    uint8_t  bootSig;
    uint32_t volID;
    char     volLab[11];
    char     filSysType[8];
    uint8_t  bootCode[420];
    uint16_t signature;

    [[nodiscard]] constexpr bool isValid() const noexcept {
        return signature == 0xAA55 && bytesPerSec != 0 && secPerClus != 0;
    }

    [[nodiscard]] constexpr uint32_t fatSize() const noexcept {
        return fatSz16 != 0 ? fatSz16 : fatSz32;
    }

    [[nodiscard]] constexpr uint32_t firstDataSector() const noexcept {
        uint32_t rootDirSectors = ((static_cast<uint32_t>(rootEntCnt) * 32) + (bytesPerSec - 1)) / bytesPerSec;
        return rsvdSecCnt + (numFATs * fatSize()) + rootDirSectors;
    }

    [[nodiscard]] constexpr uint32_t clusterToLBA(uint32_t cluster) const noexcept {
        return firstDataSector() + (cluster - 2) * secPerClus;
    }
};
#pragma pack(pop)

class ClusterChainReader {
public:
    explicit ClusterChainReader(const BootRecord& bpb) noexcept : bpb_(bpb) {}

    [[nodiscard]] static constexpr uint32_t extractNextCluster(std::span<const uint8_t> fatSector,
                                                               uint32_t cluster,
                                                               uint16_t bytesPerSec) noexcept {
        uint32_t entOffset = (cluster * 4) % bytesPerSec;
        if (entOffset + sizeof(uint32_t) > fatSector.size()) return 0x0FFFFFFF;

        uint32_t rawEntry = 0;
        for (size_t i = 0; i < 4; ++i) {
            rawEntry |= static_cast<uint32_t>(fatSector[entOffset + i]) << (i * 8);
        }
        return rawEntry & 0x0FFFFFFF;
    }

    [[nodiscard]] static constexpr bool isEndOfChain(uint32_t cluster) noexcept {
        return cluster >= 0x0FFFFFF8;
    }

private:
    BootRecord bpb_;
};

} // namespace fat32
