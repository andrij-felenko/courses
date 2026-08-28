#include <iostream>
#include <iomanip>
#include <cstdint>
#include <string_view>
#include <chrono>
#include <format>

// ── Типи та переліки в C++20 ───────────────────────────────────────────────
enum class VideoCodec {
    RawBayer,
    Mjpeg,
    H264Avc,
    H265Hevc
};

enum class LightingMode {
    Day,
    NightIr
};

// ── Параметри конфігурації відеосистеми ────────────────────────────────────
struct VideoSystemConfig {
    uint32_t width{1920};
    uint32_t height{1080};
    uint32_t fps{30};
    uint8_t  bppRaw{10};
    VideoCodec codec{VideoCodec::H264Avc};
    uint8_t  refFrames{4};
    LightingMode lightMode{LightingMode::NightIr};
    double   irOpticalWatts{1.0};
    double   irLedEfficiency{0.30};
    double   socBasePowerWatts{0.50};
    double   vpuPowerWatts{0.30};
    double   sensorPowerWatts{0.20};
    double   radioTxPowerWatts{1.10};
    double   batteryCapacityWattHours{37.0};
    double   edgeAiDutyCycle{0.005};
};

// ── Результати розрахунку ──────────────────────────────────────────────────
struct VideoBudgetResult {
    double rawSensorMbps{0.0};
    double yuv420FrameMegabytes{0.0};
    double compressedBitrateMbps{0.0};
    double dramBandwidthMegabytesPerSec{0.0};
    double minRamAllocationMegabytes{0.0};
    double totalPowerDayWatts{0.0};
    double totalPowerNightWatts{0.0};
    std::chrono::duration<double, std::ratio<3600>> streamingAutonomyHours{0};
    std::chrono::duration<double, std::ratio<86400>> edgeAiAutonomyDays{0};
};

// ── Модуль розрахунку відеотракту ──────────────────────────────────────────
class VideoBudgetCalculator {
public:
    [[nodiscard]] static constexpr VideoBudgetResult evaluate(const VideoSystemConfig& cfg) noexcept {
        VideoBudgetResult res{};

        const auto totalPixelsSec = static_cast<double>(cfg.width) * cfg.height * cfg.fps;

        // 1. Сирий піксельний потік
        res.rawSensorMbps = (totalPixelsSec * cfg.bppRaw) / 1'000'000.0;

        // Розмір одного кадру YUV420 (1.5 байти на піксель)
        const double frameBytes = static_cast<double>(cfg.width) * cfg.height * 1.5;
        res.yuv420FrameMegabytes = frameBytes / (1024.0 * 1024.0);

        // 2. Бітрейт стисненого потоку
        const double yuvRawMbps = (totalPixelsSec * 12.0) / 1'000'000.0;
        switch (cfg.codec) {
            case VideoCodec::RawBayer:
                res.compressedBitrateMbps = res.rawSensorMbps;
                break;
            case VideoCodec::Mjpeg:
                res.compressedBitrateMbps = yuvRawMbps / 10.0;
                break;
            case VideoCodec::H264Avc:
                res.compressedBitrateMbps = yuvRawMbps / 85.0;
                break;
            case VideoCodec::H265Hevc:
                res.compressedBitrateMbps = yuvRawMbps / 160.0;
                break;
        }

        // 3. Трафік системної пам'яті DRAM (ISP write + VPU read + DPB traffic + Bitstream write)
        const double ispWriteMbs = (frameBytes * cfg.fps) / (1024.0 * 1024.0);
        const double vpuReadMbs = ispWriteMbs;
        const double dpbTrafficMbs = (cfg.codec == VideoCodec::H264Avc || cfg.codec == VideoCodec::H265Hevc) 
                                     ? (ispWriteMbs * 2.0) : 0.0;
        const double bitstreamMbs = (res.compressedBitrateMbps * 1'000'000.0 / 8.0) / (1024.0 * 1024.0);

        res.dramBandwidthMegabytesPerSec = ispWriteMbs + vpuReadMbs + dpbTrafficMbs + bitstreamMbs;

        // 4. Пам'ять під буфери кадру
        const uint32_t bufferCount = 2 + (cfg.codec >= VideoCodec::H264Avc ? cfg.refFrames : 1) + 1;
        res.minRamAllocationMegabytes = bufferCount * res.yuv420FrameMegabytes;

        // 5. Електрична потужність
        const double irElectricalWatts = (cfg.irLedEfficiency > 0.05) 
            ? (cfg.irOpticalWatts / cfg.irLedEfficiency) : 0.0;
        const double baseActiveWatts = cfg.socBasePowerWatts + cfg.vpuPowerWatts + cfg.sensorPowerWatts;

        res.totalPowerDayWatts = baseActiveWatts + cfg.radioTxPowerWatts;
        res.totalPowerNightWatts = res.totalPowerDayWatts + irElectricalWatts;

        // 6. Автономність
        const double avgStreamingWatts = (res.totalPowerDayWatts + res.totalPowerNightWatts) / 2.0;
        res.streamingAutonomyHours = std::chrono::duration<double, std::ratio<3600>>(
            cfg.batteryCapacityWattHours / avgStreamingWatts
        );

        constexpr double edgeAiSleepWatts = 0.030; // 30 мВт черговий режим
        const double edgeAiActiveWatts = baseActiveWatts + cfg.radioTxPowerWatts;
        const double edgeAiAvgWatts = (cfg.edgeAiDutyCycle * edgeAiActiveWatts) + 
                                      ((1.0 - cfg.edgeAiDutyCycle) * edgeAiSleepWatts);

        res.edgeAiAutonomyDays = std::chrono::duration<double, std::ratio<86400>>(
            (cfg.batteryCapacityWattHours / edgeAiAvgWatts) / 24.0
        );

        return res;
    }
};

int main() {
    constexpr VideoSystemConfig config1080p{
        .width = 1920,
        .height = 1080,
        .fps = 30,
        .bppRaw = 10,
        .codec = VideoCodec::H264Avc,
        .refFrames = 4,
        .lightMode = LightingMode::NightIr,
        .irOpticalWatts = 1.0,
        .irLedEfficiency = 0.30,
        .socBasePowerWatts = 0.50,
        .vpuPowerWatts = 0.30,
        .sensorPowerWatts = 0.20,
        .radioTxPowerWatts = 1.10,
        .batteryCapacityWattHours = 37.0,
        .edgeAiDutyCycle = 0.005
    };

    const auto res = VideoBudgetCalculator::evaluate(config1080p);

    std::cout << "=== АУДИТ БЮДЖЕТУ ВІДЕОСИСТЕМИ (C++20 Модель) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "1. Сирий піксельний потік сенсора (10-bit RAW): " << res.rawSensorMbps << " Мбіт/с\n";
    std::cout << "2. Бітрейт стисненого відеопотоку H.264:        " << res.compressedBitrateMbps << " Мбіт/с\n";
    std::cout << "3. Навантаження на шину DRAM (AXI Bandwidth):   " << res.dramBandwidthMegabytesPerSec << " МБ/с\n";
    std::cout << "4. Мінімальний розмір пулу кадрових буферів:    " << res.minRamAllocationMegabytes << " МБ\n";
    std::cout << "5. Споживання енергії (Денний режим):           " << res.totalPowerDayWatts << " Вт\n";
    std::cout << "6. Споживання енергії (Нічний режим з ІЧ):      " << res.totalPowerNightWatts << " Вт\n";
    std::cout << "7. Автономність (Хмарний безперервний стрім):   " << res.streamingAutonomyHours.count() << " годин\n";
    std::cout << "8. Автономність (Edge AI з подійною передачею): " << res.edgeAiAutonomyDays.count() << " діб\n";

    return 0;
}
