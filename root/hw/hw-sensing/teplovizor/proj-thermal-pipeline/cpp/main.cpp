#include <cstdint>
#include <vector>
#include <array>
#include <span>
#include <algorithm>
#include <cmath>

struct Rgb888 {
    uint8_t r{0};
    uint8_t g{0};
    uint8_t b{0};
};

class ThermalPipeline {
public:
    static constexpr size_t Width = 160;
    static constexpr size_t Height = 120;
    static constexpr size_t PixelCount = Width * Height;
    static constexpr size_t HistBins = 16384;
    static constexpr uint32_t PlateauLimit = 20;

    ThermalPipeline() : globalBaseline_(8192.0f) {
        gain_.fill(1.0f);
        offset_.fill(0);
        shutter_.fill(0);
        badMask_.fill(0);
        initIronbowLut();
    }

    void updateShutter(std::span<const uint16_t, PixelCount> rawShutterFrame) noexcept {
        for (size_t i = 0; i < PixelCount; ++i) {
            shutter_[i] = static_cast<int32_t>(rawShutterFrame[i]);
        }
    }

    void setBadPixel(size_t x, size_t y, bool isBad) noexcept {
        if (x < Width && y < Height) {
            badMask_[y * Width + x] = isBad ? 1 : 0;
        }
    }

    void setGain(size_t x, size_t y, float gainVal) noexcept {
        if (x < Width && y < Height) {
            gain_[y * Width + x] = gainVal;
        }
    }

    void processFrame(std::span<const uint16_t, PixelCount> rawFrame,
                      std::span<Rgb888, PixelCount> rgbOutput) noexcept {
        std::array<float, PixelCount> nucBuffer;
        std::array<float, PixelCount> bprBuffer;
        std::array<uint8_t, PixelCount> grayBuffer;

        applyNuc(rawFrame, nucBuffer);
        replaceBadPixels(nucBuffer, bprBuffer);
        plateauEqualization(bprBuffer, grayBuffer);
        applyColormap(grayBuffer, rgbOutput);
    }

private:
    void initIronbowLut() noexcept {
        for (size_t i = 0; i < 256; ++i) {
            const float x = static_cast<float>(i) / 255.0f;
            float r{0.0f}, g{0.0f}, b{0.0f};

            if (x < 0.25f) {
                const float t = x / 0.25f;
                b = t;
            } else if (x < 0.50f) {
                const float t = (x - 0.25f) / 0.25f;
                r = t;
                b = 1.0f - 0.5f * t;
            } else if (x < 0.75f) {
                const float t = (x - 0.50f) / 0.25f;
                r = 1.0f;
                g = t;
                b = 0.5f * (1.0f - t);
            } else {
                const float t = (x - 0.75f) / 0.25f;
                r = 1.0f;
                g = 1.0f;
                b = t;
            }

            ironbowLut_[i] = Rgb888{
                static_cast<uint8_t>(std::clamp(r * 255.0f, 0.0f, 255.0f)),
                static_cast<uint8_t>(std::clamp(g * 255.0f, 0.0f, 255.0f)),
                static_cast<uint8_t>(std::clamp(b * 255.0f, 0.0f, 255.0f))
            };
        }
    }

    void applyNuc(std::span<const uint16_t, PixelCount> rawIn,
                  std::span<float, PixelCount> nucOut) const noexcept {
        for (size_t i = 0; i < PixelCount; ++i) {
            const float diff = static_cast<float>(static_cast<int32_t>(rawIn[i]) - shutter_[i]);
            nucOut[i] = diff * gain_[i] + globalBaseline_;
        }
    }

    void replaceBadPixels(std::span<const float, PixelCount> imgIn,
                          std::span<float, PixelCount> imgOut) const noexcept {
        for (size_t y = 0; y < Height; ++y) {
            for (size_t x = 0; x < Width; ++x) {
                const size_t idx = y * Width + x;
                if (badMask_[idx] == 0) {
                    imgOut[idx] = imgIn[idx];
                    continue;
                }

                float sum = 0.0f;
                int count = 0;

                for (int dy = -1; dy <= 1; ++dy) {
                    const int ny = static_cast<int>(y) + dy;
                    if (ny < 0 || ny >= static_cast<int>(Height)) continue;

                    for (int dx = -1; dx <= 1; ++dx) {
                        if (dx == 0 && dy == 0) continue;
                        const int nx = static_cast<int>(x) + dx;
                        if (nx < 0 || nx >= static_cast<int>(Width)) continue;

                        const size_t nidx = static_cast<size_t>(ny) * Width + static_cast<size_t>(nx);
                        if (badMask_[nidx] == 0) {
                            sum += imgIn[nidx];
                            ++count;
                        }
                    }
                }

                imgOut[idx] = (count > 0) ? (sum / static_cast<float>(count)) : globalBaseline_;
            }
        }
    }

    void plateauEqualization(std::span<const float, PixelCount> imgIn,
                             std::span<uint8_t, PixelCount> img8bitOut) const noexcept {
        std::array<uint32_t, HistBins> hist{};
        std::array<uint32_t, HistBins> cdf{};

        for (size_t i = 0; i < PixelCount; ++i) {
            const int bin = std::clamp(static_cast<int>(imgIn[i]), 0, static_cast<int>(HistBins - 1));
            hist[bin]++;
        }

        for (uint32_t& h : hist) {
            if (h > PlateauLimit) {
                h = PlateauLimit;
            }
        }

        uint32_t accum = 0;
        for (size_t b = 0; b < HistBins; ++b) {
            accum += hist[b];
            cdf[b] = accum;
        }

        const uint32_t totalClipped = std::max(cdf.back(), 1u);

        for (size_t i = 0; i < PixelCount; ++i) {
            const int bin = std::clamp(static_cast<int>(imgIn[i]), 0, static_cast<int>(HistBins - 1));
            const uint32_t val = (cdf[bin] * 255u) / totalClipped;
            img8bitOut[i] = static_cast<uint8_t>(std::min(val, 255u));
        }
    }

    void applyColormap(std::span<const uint8_t, PixelCount> img8bitIn,
                       std::span<Rgb888, PixelCount> rgbOut) const noexcept {
        for (size_t i = 0; i < PixelCount; ++i) {
            rgbOut[i] = ironbowLut_[img8bitIn[i]];
        }
    }

    std::array<float, PixelCount> gain_;
    std::array<int32_t, PixelCount> offset_;
    std::array<int32_t, PixelCount> shutter_;
    std::array<uint8_t, PixelCount> badMask_;
    std::array<Rgb888, 256> ironbowLut_;
    float globalBaseline_;
};
