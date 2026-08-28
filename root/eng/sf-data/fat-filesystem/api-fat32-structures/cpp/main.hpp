#pragma once

#include <cstdint>
#include <string_view>
#include <span>

namespace fat32 {

#pragma pack(push, 1)

struct alignas(1) BootSector {
    uint8_t  jmpBoot[3];
    char     oemName[8];
    uint16_t bytesPerSector;
    uint8_t  sectorsPerCluster;
    uint16_t reservedSectorCount;
    uint8_t  numFATs;
    uint16_t rootEntryCount;
    uint16_t totalSectors16;
    uint8_t  mediaType;
    uint16_t fatSize16;
    uint16_t sectorsPerTrack;
    uint16_t headCount;
    uint32_t hiddenSectors;
    uint32_t totalSectors32;

    /* FAT32 Extended Fields */
    uint32_t fatSize32;
    uint16_t extFlags;
    uint16_t fsVersion;
    uint32_t rootCluster;
    uint16_t fsInfoSector;
    uint16_t backupBootSector;
    uint8_t  reserved[12];
    uint8_t  driveNumber;
    uint8_t  reserved1;
    uint8_t  bootSignature;
    uint32_t volumeID;
    char     volumeLabel[11];
    char     fileSystemType[8];
    uint8_t  bootCode[420];
    uint16_t bootSignatureEnd;

    [[nodiscard]] constexpr uint32_t totalSectors() const noexcept {
        return totalSectors16 != 0 ? totalSectors16 : totalSectors32;
    }

    [[nodiscard]] constexpr uint32_t clusterBytes() const noexcept {
        return static_cast<uint32_t>(bytesPerSector) * sectorsPerCluster;
    }
};

struct alignas(1) FSInfo {
    uint32_t leadSignature;     // 0x41615252
    uint8_t  reserved1[480];
    uint32_t structSignature;   // 0x61417272
    uint32_t freeClusterCount;
    uint32_t nextFreeCluster;
    uint8_t  reserved2[12];
    uint32_t trailSignature;    // 0xAA550000

    [[nodiscard]] constexpr bool isValid() const noexcept {
        return leadSignature == 0x41615252 &&
               structSignature == 0x61417272 &&
               trailSignature == 0xAA550000;
    }
};

struct alignas(1) DirEntry {
    char     name[8];
    char     ext[3];
    uint8_t  attributes;
    uint8_t  ntReserved;
    uint8_t  creationTimeTenth;
    uint16_t creationTime;
    uint16_t creationDate;
    uint16_t lastAccessDate;
    uint16_t firstClusterHigh;
    uint16_t writeTime;
    uint16_t writeDate;
    uint16_t firstClusterLow;
    uint32_t fileSize;

    [[nodiscard]] constexpr uint32_t firstCluster() const noexcept {
        return (static_cast<uint32_t>(firstClusterHigh) << 16) | firstClusterLow;
    }

    [[nodiscard]] constexpr bool isDirectory() const noexcept {
        return (attributes & 0x10) != 0;
    }

    [[nodiscard]] constexpr bool isLFN() const noexcept {
        return (attributes & 0x0F) == 0x0F;
    }

    [[nodiscard]] constexpr bool isDeleted() const noexcept {
        return static_cast<uint8_t>(name[0]) == 0xE5;
    }

    [[nodiscard]] constexpr bool isEndOfDir() const noexcept {
        return static_cast<uint8_t>(name[0]) == 0x00;
    }
};

struct alignas(1) LFNEntry {
    uint8_t  order;
    uint16_t name1[5];
    uint8_t  attributes;        // 0x0F
    uint8_t  type;              // 0x00
    uint8_t  checksum;
    uint16_t name2[6];
    uint16_t firstClusterLow;   // 0x0000
    uint16_t name3[2];

    [[nodiscard]] constexpr bool isLast() const noexcept {
        return (order & 0x40) != 0;
    }

    [[nodiscard]] constexpr uint8_t sequenceNumber() const noexcept {
        return order & 0x1F;
    }
};

#pragma pack(pop)

} // namespace fat32
