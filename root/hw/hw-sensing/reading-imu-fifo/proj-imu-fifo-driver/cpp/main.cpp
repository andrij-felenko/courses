#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <atomic>
#include <algorithm>

namespace imu {

inline constexpr uint8_t REG_DEVICE_CONFIG     = 0x11;
inline constexpr uint8_t REG_INT_CONFIG        = 0x14;
inline constexpr uint8_t REG_FIFO_CONFIG       = 0x16;
inline constexpr uint8_t REG_FIFO_DATA         = 0x30;
inline constexpr uint8_t REG_SIGNAL_PATH_RESET = 0x4B;
inline constexpr uint8_t REG_PWR_MGMT0         = 0x4E;
inline constexpr uint8_t REG_GYRO_CONFIG0      = 0x4F;
inline constexpr uint8_t REG_ACCEL_CONFIG0     = 0x50;
inline constexpr uint8_t REG_FIFO_CONFIG1      = 0x5F;
inline constexpr uint8_t REG_FIFO_CONFIG2      = 0x60;
inline constexpr uint8_t REG_FIFO_CONFIG3      = 0x61;

inline constexpr uint8_t HEADER_ACCEL_BIT     = 0x40;
inline constexpr uint8_t HEADER_GYRO_BIT      = 0x20;
inline constexpr uint8_t HEADER_EMPTY_MARKER  = 0x80;

inline constexpr size_t WATERMARK_FRAMES       = 10;
inline constexpr size_t FRAME_SIZE_BYTES       = 16;
inline constexpr size_t DMA_BUFFER_SIZE        = WATERMARK_FRAMES * FRAME_SIZE_BYTES;

inline constexpr float ACCEL_SCALE_16G = (16.0f / 32768.0f) * 9.80665f;
inline constexpr float GYRO_SCALE_2000DPS = (2000.0f / 32768.0f) * 0.0174532925f;

enum class DriverError {
    BusError,
    DmaBusy,
    SyncLoss,
    BufferOverflow
};

struct MotionSample {
    std::array<float, 3> accel{};
    std::array<float, 3> gyro{};
    float                temp_c{0.0f};
    uint32_t             timestamp_us{0};
};

class ISpiBusDma {
public:
    virtual ~ISpiBusDma() = default;
    virtual void write_register(uint8_t reg, uint8_t val) = 0;
    virtual uint8_t read_register(uint8_t reg) = 0;
    virtual void start_dma_transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx) = 0;
    virtual void delay_ms(uint32_t ms) = 0;
};

class ImuFifoDriver {
public:
    explicit ImuFifoDriver(ISpiBusDma &bus) : bus_{bus} {
        tx_dummy_.fill(0x00);
        tx_dummy_[0] = REG_FIFO_DATA | 0x80; // SPI Read command
    }

    std::expected<void, DriverError> initialize() {
        // Скидання мікросхеми
        bus_.write_register(REG_DEVICE_CONFIG, 0x01);
        bus_.delay_ms(10);

        // Увімкнення датчиків у режим Low-Noise
        bus_.write_register(REG_PWR_MGMT0, 0x0F);
        bus_.delay_ms(50);

        // Налаштування ODR 1000 Гц
        bus_.write_register(REG_ACCEL_CONFIG0, 0x06);
        bus_.write_register(REG_GYRO_CONFIG0, 0x06);

        // Очищення FIFO
        bus_.write_register(REG_SIGNAL_PATH_RESET, 0x02);
        bus_.delay_ms(2);

        // Встановлення порогу Watermark (160 B)
        constexpr uint16_t wm = static_cast<uint16_t>(DMA_BUFFER_SIZE);
        bus_.write_register(REG_FIFO_CONFIG2, static_cast<uint8_t>(wm & 0xFF));
        bus_.write_register(REG_FIFO_CONFIG3, static_cast<uint8_t>((wm >> 8) & 0x0F));

        // Конфігурація кадру Packet 3 (16 B) та увімкнення режиму Stream
        bus_.write_register(REG_FIFO_CONFIG1, 0x07);
        bus_.write_register(REG_FIFO_CONFIG, 0x40);

        return {};
    }

    void handle_watermark_interrupt() {
        if (dma_in_progress_.exchange(true, std::memory_order_acquire)) {
            return;
        }

        auto &target_buf = active_buf_is_pong_.load(std::memory_order_relaxed) ? 
                           rx_buf_pong_ : rx_buf_ping_;

        bus_.start_dma_transfer(
            std::span<const uint8_t>{tx_dummy_.data(), DMA_BUFFER_SIZE + 1},
            std::span<uint8_t>{target_buf.data(), DMA_BUFFER_SIZE + 1}
        );
    }

    void handle_dma_complete() {
        dma_in_progress_.store(false, std::memory_order_release);
        data_ready_.store(true, std::memory_order_release);
        
        bool current = active_buf_is_pong_.load(std::memory_order_relaxed);
        active_buf_is_pong_.store(!current, std::memory_order_relaxed);
    }

    std::expected<size_t, DriverError> parse_batch(std::span<MotionSample> out_samples) {
        if (!data_ready_.exchange(false, std::memory_order_acq_rel)) {
            return 0;
        }

        const auto &ready_buf = active_buf_is_pong_.load(std::memory_order_relaxed) ? 
                                rx_buf_ping_ : rx_buf_pong_;

        // Пропускаємо 1-й dummy-байт відповіді SPI
        const uint8_t *stream = ready_buf.data() + 1;
        size_t parsed_count = 0;
        size_t byte_offset = 0;

        while (byte_offset + FRAME_SIZE_BYTES <= DMA_BUFFER_SIZE && parsed_count < out_samples.size()) {
            uint8_t header = stream[byte_offset];

            if (header & HEADER_EMPTY_MARKER) {
                break;
            }

            if ((header & (HEADER_ACCEL_BIT | HEADER_GYRO_BIT)) == (HEADER_ACCEL_BIT | HEADER_GYRO_BIT)) {
                int16_t ax = static_cast<int16_t>((stream[byte_offset + 1] << 8) | stream[byte_offset + 2]);
                int16_t ay = static_cast<int16_t>((stream[byte_offset + 3] << 8) | stream[byte_offset + 4]);
                int16_t az = static_cast<int16_t>((stream[byte_offset + 5] << 8) | stream[byte_offset + 6]);

                int16_t gx = static_cast<int16_t>((stream[byte_offset + 7] << 8) | stream[byte_offset + 8]);
                int16_t gy = static_cast<int16_t>((stream[byte_offset + 9] << 8) | stream[byte_offset + 10]);
                int16_t gz = static_cast<int16_t>((stream[byte_offset + 11] << 8) | stream[byte_offset + 12]);

                int8_t temp = static_cast<int8_t>(stream[byte_offset + 13]);
                uint16_t ts = static_cast<uint16_t>((stream[byte_offset + 14] << 8) | stream[byte_offset + 15]);

                out_samples[parsed_count] = MotionSample{
                    .accel = {ax * ACCEL_SCALE_16G, ay * ACCEL_SCALE_16G, az * ACCEL_SCALE_16G},
                    .gyro  = {gx * GYRO_SCALE_2000DPS, gy * GYRO_SCALE_2000DPS, gz * GYRO_SCALE_2000DPS},
                    .temp_c = (temp / 2.07f) + 25.0f,
                    .timestamp_us = static_cast<uint32_t>(ts) * 16
                };

                parsed_count++;
                byte_offset += FRAME_SIZE_BYTES;
            } else {
                byte_offset++; // Пошук втраченої синхронізації
            }
        }

        return parsed_count;
    }

private:
    ISpiBusDma &bus_;
    std::array<uint8_t, DMA_BUFFER_SIZE + 1> tx_dummy_{};
    std::array<uint8_t, DMA_BUFFER_SIZE + 1> rx_buf_ping_{};
    std::array<uint8_t, DMA_BUFFER_SIZE + 1> rx_buf_pong_{};
    
    std::atomic<bool> active_buf_is_pong_{false};
    std::atomic<bool> dma_in_progress_{false};
    std::atomic<bool> data_ready_{false};
};

} // namespace imu
