#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <string_view>

// Модель бюджету відеотракту. Усі «мега» десяткові (10^6) — так їх рахують
// даташити шин, кодеків і радіо; змішувати з двійковими МіБ не можна.
namespace video {

enum class Codec {
    RawBayer,  // без стиснення: сирий Bayer прямо в пам'ять
    Mjpeg,     // лише внутрішньокадрове стиснення, без опорних кадрів
    H264Avc,   // міжкадрове передбачення, потрібен DPB
    H265Hevc
};

struct Config {
    std::uint32_t width{1920};
    std::uint32_t height{1080};
    std::uint32_t fps{30};
    std::uint8_t  rawDepthBits{10};   // розрядність АЦП матриці
    Codec         codec{Codec::H264Avc};
    std::uint8_t  refFrames{4};       // глибина DPB для міжкадрових кодеків

    double irOpticalW{0.0};           // потрібна ОПТИЧНА потужність ІЧ, Вт (0 — немає)
    double irLedEfficiency{0.30};     // електрооптичний ККД світлодіода

    double socBaseW{0.50};            // ядро SoC з контролером пам'яті
    double vpuW{0.30};                // апаратний кодек або NPU під час роботи
    double sensorW{0.20};             // матриця з аналоговим трактом
    double radioTxW{1.10};            // радіо в режимі передачі
    double standbyW{0.030};           // чергова схема під час сну

    double batteryWh{37.0};
    double edgeDutyCycle{0.005};      // частка часу активності в Edge AI
};

using Hours = std::chrono::duration<double, std::ratio<3600>>;
using Days  = std::chrono::duration<double, std::ratio<86400>>;

struct Budget {
    double rawSensorMbps{};       // сирий потік із матриці, Мбіт/с
    double yuvFrameMB{};          // один кадр YUV420, МБ
    double codecMbps{};           // бітрейт після кодека, Мбіт/с
    double dramMBps{};            // сумарний трафік системної шини, МБ/с

    std::uint32_t frameBuffers{}; // скільки кадрових буферів тримаємо одночасно
    double ramPoolMB{};           // пул під ці буфери, МБ

    double irElectricalW{};       // що ІЧ бере від джерела живлення
    double powerDayW{};
    double powerNightW{};
    double powerStreamW{};        // середнє за добу при стрімінгу
    Hours  streamingAutonomy{};
    double powerEdgeW{};          // середнє за добу в Edge AI
    Days   edgeAutonomy{};
};

enum class ConfigError {
    Geometry,      // нульова або непарна роздільність
    Fps,
    RawDepth,
    RefFrames,
    IrEfficiency,
    Power,
    Battery,
    DutyCycle
};

[[nodiscard]] std::string_view describe(ConfigError error) noexcept;
[[nodiscard]] std::string_view name(Codec codec) noexcept;

// Питомий бітрейт кодека для типової сцени відеоспостереження, біт/піксель.
[[nodiscard]] double bitsPerPixel(Codec codec, std::uint8_t rawDepthBits) noexcept;

// Або повний бюджет, або причина, чому конфігурація неприйнятна.
// Помилку неможливо пропустити повз увагу, як -1 із errno.
[[nodiscard]] std::expected<Budget, ConfigError> evaluate(const Config& cfg) noexcept;

}  // namespace video
