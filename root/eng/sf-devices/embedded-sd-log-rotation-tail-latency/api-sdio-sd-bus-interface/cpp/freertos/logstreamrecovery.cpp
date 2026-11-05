#include "ff.h"
#include <cstdint>
#include <cstddef>
#include <array>

class LogStreamRecovery {
public:
    static constexpr std::size_t kSectorSize = 512;

    static std::uint32_t recoverBoundary(FIL* file, std::uint64_t& outLastSeq) {
        alignas(4) std::array<std::uint8_t, kSectorSize> sectorBuf{};
        UINT bytesRead = 0;
        std::uint32_t validOffset = 0;
        std::uint64_t expectedSeq = 0;
        outLastSeq = 0;

        f_lseek(file, 0);

        while (f_read(file, sectorBuf.data(), kSectorSize, &bytesRead) == FR_OK && bytesRead == kSectorSize) {
            bool sectorValid = true;

            for (std::size_t offset = 0; offset < kSectorSize; offset += sizeof(SdioDmaStreamer::LogPacket)) {
                const auto* pkt = reinterpret_cast<const SdioDmaStreamer::LogPacket*>(&sectorBuf[offset]);

                if (pkt->magic != SdioDmaStreamer::kPacketMagic) {
                    sectorValid = false;
                    break;
                }

                if (expectedSeq > 0 && pkt->seqNum != expectedSeq + 1) {
                    sectorValid = false;
                    break;
                }

                std::uint32_t calcCrc = computeCrc32(reinterpret_cast<const std::uint8_t*>(pkt),
                                                     sizeof(SdioDmaStreamer::LogPacket) - sizeof(std::uint32_t));
                if (calcCrc != pkt->crc32) {
                    sectorValid = false;
                    break;
                }

                expectedSeq = pkt->seqNum;
                outLastSeq = expectedSeq;
                validOffset += sizeof(SdioDmaStreamer::LogPacket);
            }

            if (!sectorValid) break;
        }

        f_lseek(file, validOffset);
        return validOffset;
    }

private:
    static std::uint32_t computeCrc32(const std::uint8_t* data, std::size_t len) {
        std::uint32_t crc = 0xFFFFFFFFU;
        for (std::size_t i = 0; i < len; ++i) {
            crc ^= data[i];
            for (std::uint8_t b = 0; b < 8; ++b) {
                crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
            }
        }
        return ~crc;
    }
};
