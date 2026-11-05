#include "ff.h"
#include "diskio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <array>
#include <atomic>
#include <limits>

extern "C" void SCB_CleanDCache_by_Addr(uint32_t *addr, int32_t dsize);

class SdioDmaStreamer {
public:
    static constexpr std::uint32_t kPacketMagic = 0x53444C47U; // "SDLG"
    static constexpr std::size_t kSectorSize = 512;
    static constexpr std::size_t kBufferSectors = 32;
    static constexpr std::size_t kBufferSizeBytes = kSectorSize * kBufferSectors; // 16384 байти
    static constexpr std::size_t kCacheLineSize = 32;

    struct alignas(4) LogPacket {
        std::uint32_t magic;
        std::uint64_t seqNum;
        std::uint32_t timestampMs;
        std::uint16_t sensorId;
        std::uint16_t payloadLen;
        std::uint8_t  payload[40];
        std::uint32_t crc32;
    };

    explicit SdioDmaStreamer(TaskHandle_t workerTask, std::uint32_t startLba)
        : m_workerTask(workerTask), m_currentLba(startLba) {}

    bool submit(std::uint16_t sensorId, const void* payload, std::uint16_t len, std::uint32_t timestampMs) {
        if (len > 40) return false;

        if (m_fillBytes + sizeof(LogPacket) > kBufferSizeBytes) {
            if (m_dmaBusy.load(std::memory_order_relaxed)) {
                ++m_dropCount;
                return false;
            }

            const std::size_t fullIdx = m_activeIdx;
            m_activeIdx ^= 1;
            m_fillBytes = 0;

            xTaskNotify(m_workerTask, static_cast<std::uint32_t>(fullIdx), eSetValueWithOverwrite);
        }

        LogPacket pkt{};
        pkt.magic = kPacketMagic;
        pkt.seqNum = ++m_nextSeq;
        pkt.timestampMs = timestampMs;
        pkt.sensorId = sensorId;
        pkt.payloadLen = len;
        if (payload && len > 0) {
            std::memcpy(pkt.payload, payload, len);
        }
        pkt.crc32 = computeCrc32(reinterpret_cast<const std::uint8_t*>(&pkt), sizeof(pkt) - sizeof(std::uint32_t));

        std::uint8_t* dst = &m_buffers[m_activeIdx][m_fillBytes];
        std::memcpy(dst, &pkt, sizeof(pkt));
        m_fillBytes += sizeof(pkt);

        return true;
    }

    void onDmaCompleteFromIsr(BaseType_t* higherPriorityTaskWoken) {
        m_dmaBusy.store(false, std::memory_order_release);
        vTaskNotifyGiveFromISR(m_workerTask, higherPriorityTaskWoken);
    }

    void workerLoop() {
        std::uint32_t bufToFlush = 0;

        for (;;) {
            if (xTaskNotifyWait(0, std::numeric_limits<std::uint32_t>::max(), &bufToFlush, portMAX_DELAY) == pdTRUE) {
                m_dmaBusy.store(true, std::memory_order_release);

                std::uint8_t* flushPtr = m_buffers[bufToFlush].data();

                // Синхронізація L1 D-Cache перед початком шинної операції DMA
                SCB_CleanDCache_by_Addr(reinterpret_cast<std::uint32_t*>(flushPtr), kBufferSizeBytes);

                DRESULT dr = disk_write(0, flushPtr, m_currentLba, kBufferSectors);
                if (dr == RES_OK) {
                    if (ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(1000)) == 0) {
                        m_dmaBusy.store(false, std::memory_order_release);
                    } else {
                        m_currentLba += kBufferSectors;
                    }
                } else {
                    m_dmaBusy.store(false, std::memory_order_release);
                }
            }
        }
    }

    std::uint32_t dropCount() const { return m_dropCount; }
    std::uint64_t nextSequenceNumber() const { return m_nextSeq; }

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

    alignas(kCacheLineSize) std::array<std::array<std::uint8_t, kBufferSizeBytes>, 2> m_buffers{};
    std::size_t m_activeIdx{0};
    std::size_t m_fillBytes{0};
    std::atomic<bool> m_dmaBusy{false};
    TaskHandle_t m_workerTask{nullptr};
    std::uint64_t m_nextSeq{0};
    std::uint32_t m_dropCount{0};
    std::uint32_t m_currentLba{0};
};
