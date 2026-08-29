#include "video/budget.hpp"

#include <optional>

namespace video {
namespace {

constexpr double kMega = 1'000'000.0;

constexpr bool usesReferenceFrames(Codec codec) noexcept
{
    return codec == Codec::H264Avc || codec == Codec::H265Hevc;
}

// Валідація зібрана в одному місці: далі в розрахунку немає жодної перевірки,
// бо всі ділення вже захищені.
[[nodiscard]] std::optional<ConfigError> validate(const Config& cfg) noexcept
{
    if (cfg.width == 0 || cfg.height == 0 || cfg.width % 2 != 0 || cfg.height % 2 != 0)
        return ConfigError::Geometry;

    if (cfg.fps == 0 || cfg.fps > 240)
        return ConfigError::Fps;

    if (cfg.rawDepthBits < 8 || cfg.rawDepthBits > 16)
        return ConfigError::RawDepth;

    if (usesReferenceFrames(cfg.codec) && (cfg.refFrames == 0 || cfg.refFrames > 16))
        return ConfigError::RefFrames;

    if (cfg.irOpticalW < 0.0)
        return ConfigError::Power;

    // ККД питаємо лише тоді, коли підсвічування справді стоїть: інакше денна
    // камера спотикалася б об поле, якого ніхто не заповнював.
    if (cfg.irOpticalW > 0.0 && (cfg.irLedEfficiency < 0.05 || cfg.irLedEfficiency > 1.0))
        return ConfigError::IrEfficiency;

    if (cfg.socBaseW < 0.0 || cfg.vpuW < 0.0 || cfg.sensorW < 0.0 ||
        cfg.radioTxW < 0.0 || cfg.standbyW <= 0.0)
        return ConfigError::Power;

    if (cfg.batteryWh <= 0.0)
        return ConfigError::Battery;

    if (cfg.edgeDutyCycle <= 0.0 || cfg.edgeDutyCycle > 1.0)
        return ConfigError::DutyCycle;

    return std::nullopt;
}

}  // namespace

std::string_view describe(ConfigError error) noexcept
{
    switch (error) {
        case ConfigError::Geometry:     return "роздільність нульова або непарна (YUV420 вимагає парних сторін)";
        case ConfigError::Fps:          return "частота кадрів поза 1..240 к/с";
        case ConfigError::RawDepth:     return "розрядність матриці поза 8..16 біт";
        case ConfigError::RefFrames:    return "глибина DPB поза 1..16 кадрів";
        case ConfigError::IrEfficiency: return "ККД ІЧ-світлодіода поза 0.05..1.0";
        case ConfigError::Power:        return "від'ємна потужність або нульове споживання в черговому режимі";
        case ConfigError::Battery:      return "ємність акумулятора має бути додатною";
        case ConfigError::DutyCycle:    return "коефіцієнт заповнення Edge AI поза (0..1]";
    }
    return "невідома помилка";
}

std::string_view name(Codec codec) noexcept
{
    switch (codec) {
        case Codec::RawBayer: return "RAW Bayer";
        case Codec::Mjpeg:    return "MJPEG";
        case Codec::H264Avc:  return "H.264 (AVC)";
        case Codec::H265Hevc: return "H.265 (HEVC)";
    }
    return "?";
}

// Питомий бітрейт зміряний на сцені відеоспостереження (статичний фон, рух у
// частині кадру). 0.052 біт/піксель для H.264 — це стиснення 12 / 0.052 ≈ 230
// разів відносно сирого YUV420.
double bitsPerPixel(Codec codec, std::uint8_t rawDepthBits) noexcept
{
    switch (codec) {
        case Codec::RawBayer: return static_cast<double>(rawDepthBits);
        case Codec::Mjpeg:    return 0.750;  // лише внутрішньокадрове, ~16x
        case Codec::H264Avc:  return 0.052;
        case Codec::H265Hevc: return 0.026;  // удвічі краще за AVC на тій самій якості
    }
    return 0.0;
}

std::expected<Budget, ConfigError> evaluate(const Config& cfg) noexcept
{
    if (const auto error = validate(cfg))
        return std::unexpected{*error};

    Budget budget{};

    const double pixelsPerSec = static_cast<double>(cfg.width) * cfg.height * cfg.fps;
    const double rawFrameBytes = static_cast<double>(cfg.width) * cfg.height * cfg.rawDepthBits / 8.0;
    const double yuvFrameBytes = static_cast<double>(cfg.width) * cfg.height * 3.0 / 2.0;
    const bool   dpb = usesReferenceFrames(cfg.codec);

    // 1. Піксельний потік із матриці та розмір кадру після ISP.
    budget.rawSensorMbps = pixelsPerSec * cfg.rawDepthBits / kMega;
    budget.yuvFrameMB    = yuvFrameBytes / kMega;
    budget.codecMbps     = pixelsPerSec * bitsPerPixel(cfg.codec, cfg.rawDepthBits) / kMega;

    // 2. Трафік системної шини. Кадр перетинає її стільки разів, скільки блоків
    //    його чіпає, — і вбиває платформу саме цей множник, а не бітрейт.
    const double bitstreamBytesPerSec = budget.codecMbps * kMega / 8.0;
    if (cfg.codec == Codec::RawBayer) {
        // Сирий тракт: DMA пише кадр, споживач читає — два проходи.
        budget.dramMBps = 2.0 * rawFrameBytes * cfg.fps / kMega;
    } else {
        const double yuvBytesPerSec = yuvFrameBytes * cfg.fps;
        budget.dramMBps = (yuvBytesPerSec                            // ISP пише кадр YUV420
                           + yuvBytesPerSec                          // VPU читає його на кодування
                           + (dpb ? 2.0 * yuvBytesPerSec : 0.0)      // читання-запис опорних кадрів
                           + bitstreamBytesPerSec)                   // кодер пише бітстрім
                          / kMega;
    }

    // 3. Пул кадрових буферів: подвійна буферизація захоплення + DPB (або один
    //    робочий кадр для внутрішньокадрових кодеків) + кадр на віддачу.
    const double bufferBytes = (cfg.codec == Codec::RawBayer) ? rawFrameBytes : yuvFrameBytes;
    budget.frameBuffers = 2u + (dpb ? static_cast<std::uint32_t>(cfg.refFrames) : 1u) + 1u;
    budget.ramPoolMB    = budget.frameBuffers * bufferBytes / kMega;

    // 4. Електрика. ІЧ-підсвічування бере від джерела втричі більше, ніж світить.
    budget.irElectricalW = (cfg.irOpticalW > 0.0) ? cfg.irOpticalW / cfg.irLedEfficiency : 0.0;

    const double activeW = cfg.socBaseW + cfg.vpuW + cfg.sensorW;
    budget.powerDayW   = activeW + cfg.radioTxW;
    budget.powerNightW = budget.powerDayW + budget.irElectricalW;

    // 5. Автономність. Стрімінг: половину доби день, половину ніч.
    budget.powerStreamW      = (budget.powerDayW + budget.powerNightW) / 2.0;
    budget.streamingAutonomy = Hours{cfg.batteryWh / budget.powerStreamW};

    // Edge AI: більшість часу спимо на черговій схемі, зрідка прокидаємось на
    // інференс і коротку передачу метаданих.
    budget.powerEdgeW = cfg.edgeDutyCycle * budget.powerDayW
                      + (1.0 - cfg.edgeDutyCycle) * cfg.standbyW;
    budget.edgeAutonomy = Days{cfg.batteryWh / budget.powerEdgeW / 24.0};

    return budget;
}

}  // namespace video
