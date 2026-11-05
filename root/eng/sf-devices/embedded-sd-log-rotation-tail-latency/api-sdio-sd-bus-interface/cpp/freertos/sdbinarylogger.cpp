#include "ff.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <algorithm>
#include <array>

class SdBinaryLogger {
public:
    static constexpr std::size_t kFileCount = 4;
    static constexpr std::size_t kMaxFileSize = 10 * 1024 * 1024; // 10 МБ
    static constexpr std::size_t kSectorSize = 512;
    static constexpr std::size_t kBufferSectors = 8;
    static constexpr std::size_t kRamBufferSize = kSectorSize * kBufferSectors; // 4096 байтів

    struct alignas(4) LogRecord {
        std::uint32_t timestampMs;
        std::uint16_t eventId;
        std::uint16_t payloadLen;
        std::uint8_t  payload[56];
    };

    SdBinaryLogger() = default;

    FRESULT initPool() {
        FRESULT res = FR_OK;
        char fileName[32];

        for (std::size_t i = 0; i < kFileCount; ++i) {
            std::snprintf(fileName, sizeof(fileName), "0:/LOG_%03u.BIN", static_cast<unsigned>(i));
            res = f_open(&m_file, fileName, FA_WRITE | FA_OPEN_ALWAYS);
            if (res != FR_OK) return res;

            // Попереднє виділення суцільного блоку кластерів
            res = f_expand(&m_file, kMaxFileSize, 1);
            if (res != FR_OK && res != FR_EXIST) {
                f_close(&m_file);
                return res;
            }
            f_close(&m_file);
        }

        std::snprintf(fileName, sizeof(fileName), "0:/LOG_%03u.BIN", static_cast<unsigned>(m_currentFileIdx));
        res = f_open(&m_file, fileName, FA_WRITE | FA_OPEN_EXISTING);
        if (res == FR_OK) {
            res = f_lseek(&m_file, 0);
        }
        return res;
    }

    FRESULT writeRecord(const LogRecord& record) {
        FRESULT res = FR_OK;
        const auto* src = reinterpret_cast<const std::uint8_t*>(&record);
        std::size_t bytesLeft = sizeof(LogRecord);

        if (m_bytesWrittenInFile + m_bufferOffset + bytesLeft >= kMaxFileSize) {
            flushBuffer();
            f_sync(&m_file);
            f_close(&m_file);

            m_currentFileIdx = (m_currentFileIdx + 1) % kFileCount;
            m_bytesWrittenInFile = 0;

            char fileName[32];
            std::snprintf(fileName, sizeof(fileName), "0:/LOG_%03u.BIN", static_cast<unsigned>(m_currentFileIdx));
            res = f_open(&m_file, fileName, FA_WRITE | FA_OPEN_EXISTING);
            if (res != FR_OK) return res;

            res = f_lseek(&m_file, 0);
            if (res != FR_OK) return res;
        }

        while (bytesLeft > 0) {
            std::size_t spaceLeft = kRamBufferSize - m_bufferOffset;
            std::size_t chunk = std::min(bytesLeft, spaceLeft);

            std::memcpy(&m_ramBuffer[m_bufferOffset], src, chunk);
            m_bufferOffset += chunk;
            src += chunk;
            bytesLeft -= chunk;

            if (m_bufferOffset >= kRamBufferSize) {
                res = flushBuffer();
                if (res != FR_OK) break;
            }
        }
        return res;
    }

    FRESULT flushBuffer() {
        if (m_bufferOffset == 0) return FR_OK;

        UINT bw = 0;
        FRESULT res = f_write(&m_file, m_ramBuffer.data(), m_bufferOffset, &bw);
        if (res == FR_OK) {
            m_bytesWrittenInFile += bw;
            m_bufferOffset = 0;
        }
        return res;
    }

private:
    FIL m_file{};
    alignas(4) std::array<std::uint8_t, kRamBufferSize> m_ramBuffer{};
    std::size_t m_bufferOffset{0};
    std::size_t m_currentFileIdx{0};
    std::size_t m_bytesWrittenInFile{0};
};
