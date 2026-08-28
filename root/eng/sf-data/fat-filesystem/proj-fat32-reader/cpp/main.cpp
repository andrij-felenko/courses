#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <cstdint>
#include <cstring>
#include <optional>

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
    uint16_t signature;
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
    [[nodiscard]] constexpr bool isDirectory() const noexcept { return (attributes & 0x10) != 0; }
    [[nodiscard]] constexpr bool isLFN() const noexcept { return (attributes & 0x0F) == 0x0F; }
    [[nodiscard]] constexpr bool isVolumeLabel() const noexcept { return (attributes & 0x08) != 0; }
    [[nodiscard]] constexpr bool isDeleted() const noexcept { return static_cast<uint8_t>(name[0]) == 0xE5; }
    [[nodiscard]] constexpr bool isEndOfDir() const noexcept { return static_cast<uint8_t>(name[0]) == 0x00; }
};

struct alignas(1) LFNEntry {
    uint8_t  order;
    uint16_t name1[5];
    uint8_t  attributes;
    uint8_t  type;
    uint8_t  checksum;
    uint16_t name2[6];
    uint16_t firstClusterLow;
    uint16_t name3[2];
};
#pragma pack(pop)

class ImageReader {
public:
    explicit ImageReader(const std::string& path) {
        stream_.open(path, std::ios::binary);
    }

    [[nodiscard]] bool isOpen() const noexcept { return stream_.is_open(); }

    bool readAt(uint64_t offset, std::span<uint8_t> buffer) {
        stream_.seekg(static_cast<std::streamoff>(offset), std::ios::beg);
        stream_.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
        return stream_.gcount() == static_cast<std::streamsize>(buffer.size());
    }

private:
    std::ifstream stream_;
};

class Volume {
public:
    static std::optional<Volume> mount(const std::string& imagePath) {
        auto reader = std::make_unique<ImageReader>(imagePath);
        if (!reader->isOpen()) return std::nullopt;

        BootSector bs{};
        if (!reader->readAt(0, {reinterpret_cast<uint8_t*>(&bs), sizeof(BootSector)})) {
            return std::nullopt;
        }

        if (bs.signature != 0xAA55 || bs.bytesPerSector == 0 || bs.sectorsPerCluster == 0) {
            return std::nullopt;
        }

        return Volume(std::move(reader), bs);
    }

    void listRootDirectory() {
        uint32_t clusterBytes = static_cast<uint32_t>(bs_.bytesPerSector) * bs_.sectorsPerCluster;
        std::vector<uint8_t> clusterBuffer(clusterBytes);

        uint32_t currentCluster = bs_.rootCluster;
        std::string lfnBuffer;
        uint8_t expectedChecksum = 0;

        while (currentCluster >= 2 && currentCluster < 0x0FFFFFF8) {
            if (!readCluster(currentCluster, clusterBuffer)) break;

            auto entries = std::span<const DirEntry>(
                reinterpret_cast<const DirEntry*>(clusterBuffer.data()),
                clusterBytes / sizeof(DirEntry)
            );

            for (const auto& entry : entries) {
                if (entry.isEndOfDir()) return;
                if (entry.isDeleted()) {
                    lfnBuffer.clear();
                    continue;
                }

                if (entry.isLFN()) {
                    const auto& lfn = reinterpret_cast<const LFNEntry&>(entry);
                    expectedChecksum = lfn.checksum;

                    uint16_t rawChars[13];
                    std::memcpy(&rawChars[0], lfn.name1, 10);
                    std::memcpy(&rawChars[5], lfn.name2, 12);
                    std::memcpy(&rawChars[11], lfn.name3, 4);

                    std::string chunk;
                    for (uint16_t ch : rawChars) {
                        if (ch == 0x0000 || ch == 0xFFFF) break;
                        chunk.push_back(static_cast<char>(ch & 0xFF));
                    }
                    lfnBuffer = chunk + lfnBuffer;
                    continue;
                }

                if (entry.isVolumeLabel()) {
                    lfnBuffer.clear();
                    continue;
                }

                uint8_t actualChecksum = computeSFNChecksum(entry.name);
                std::string displayName = (!lfnBuffer.empty() && actualChecksum == expectedChecksum)
                                          ? lfnBuffer : extractSFN(entry);

                std::cout << (entry.isDirectory() ? "[DIR ] " : "[FILE] ")
                          << displayName << " | Кластер: " << entry.firstCluster()
                          << " | Розмір: " << entry.fileSize << " B\n";

                lfnBuffer.clear();
            }

            currentCluster = nextCluster(currentCluster);
        }
    }

private:
    Volume(std::unique_ptr<ImageReader> reader, const BootSector& bs)
        : reader_(std::move(reader)), bs_(bs) {
        fatStartLBA_ = bs_.reservedSectorCount;
        dataStartLBA_ = bs_.reservedSectorCount + (bs_.numFATs * bs_.fatSize32);
    }

    [[nodiscard]] uint32_t clusterToLBA(uint32_t cluster) const noexcept {
        return dataStartLBA_ + (cluster - 2) * bs_.sectorsPerCluster;
    }

    [[nodiscard]] uint32_t nextCluster(uint32_t currentCluster) {
        uint32_t fatOffset = currentCluster * 4;
        uint64_t byteOffset = static_cast<uint64_t>(fatStartLBA_) * bs_.bytesPerSector + fatOffset;

        uint32_t nextEntry = 0;
        if (!reader_->readAt(byteOffset, {reinterpret_cast<uint8_t*>(&nextEntry), sizeof(uint32_t)})) {
            return 0x0FFFFFFF;
        }
        return nextEntry & 0x0FFFFFFF;
    }

    bool readCluster(uint32_t cluster, std::span<uint8_t> buffer) {
        uint64_t byteOffset = static_cast<uint64_t>(clusterToLBA(cluster)) * bs_.bytesPerSector;
        return reader_->readAt(byteOffset, buffer);
    }

    static uint8_t computeSFNChecksum(const char name[8]) noexcept {
        uint8_t sum = 0;
        const auto* ptr = reinterpret_cast<const uint8_t*>(name);
        for (size_t i = 0; i < 11; ++i) {
            sum = static_cast<uint8_t>(((sum & 1) ? 0x80 : 0) + (sum >> 1) + ptr[i]);
        }
        return sum;
    }

    static std::string extractSFN(const DirEntry& entry) {
        std::string sfn;
        for (int i = 0; i < 8 && entry.name[i] != ' '; ++i) sfn.push_back(entry.name[i]);
        if (entry.ext[0] != ' ') {
            sfn.push_back('.');
            for (int i = 0; i < 3 && entry.ext[i] != ' '; ++i) sfn.push_back(entry.ext[i]);
        }
        return sfn;
    }

    std::unique_ptr<ImageReader> reader_;
    BootSector bs_;
    uint32_t fatStartLBA_{0};
    uint32_t dataStartLBA_{0};
};

} // namespace fat32
