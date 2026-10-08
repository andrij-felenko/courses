#include <cstdint>
#include <cstddef>

enum class FrameFormat : std::uint8_t {
    Yuv422,
    Rgb565,
    Jpeg
};

struct CameraConfig {
    std::uint16_t width{1600};
    std::uint16_t height{1200};
    FrameFormat format{FrameFormat::Jpeg};
    std::uint8_t jpegQuality{10};

    [[nodiscard]] constexpr std::size_t calculateBufferSize() const noexcept {
        const std::size_t rawPixels = static_cast<std::size_t>(width) * height;
        
        if (format == FrameFormat::Yuv422 || format == FrameFormat::Rgb565) {
            return rawPixels * 2;
        }
        
        // Для JPEG оцінюємо буфер залежно від коефіцієнта стиснення
        const std::size_t uncompressedBytes = rawPixels * 2;
        return (jpegQuality < 10) ? (uncompressedBytes / 4) : (uncompressedBytes / 10);
    }
};
