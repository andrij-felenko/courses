#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <string>
#include <cstdint>
#include <algorithm>

enum class AssetKind {
    Unknown,
    TrueTypeFont,
    TFLiteModel
};

struct EmbeddedAsset {
    std::uint32_t offset{0};
    std::uint32_t size{0};
    AssetKind kind{AssetKind::Unknown};
    std::string identifier;
};

class RomAssetScanner {
public:
    static std::vector<EmbeddedAsset> scan(std::span<const std::uint8_t> rom) {
        std::vector<EmbeddedAsset> results;
        if (rom.size() < 16) return results;

        for (std::size_t i = 0; i + 16 < rom.size(); ++i) {
            const auto window = rom.subspan(i);

            // Перевірка магічних сигнатур шрифтів TrueType / OpenType
            const bool isFont = (window[0] == 0x00 && window[1] == 0x01 && window[2] == 0x00 && window[3] == 0x00) ||
                                (std::string_view(reinterpret_cast<const char*>(window.data()), 4) == "OTTO");

            if (isFont) {
                results.push_back(EmbeddedAsset{
                    .offset = static_cast<std::uint32_t>(i),
                    .size = 0,
                    .kind = AssetKind::TrueTypeFont,
                    .identifier = "font-ttf-rom-0x" + toHex(static_cast<std::uint32_t>(i))
                });
                i += 256;
                continue;
            }

            // Перевірка сигнатури моделі TensorFlow Lite
            if (window.size() >= 8 &&
                std::string_view(reinterpret_cast<const char*>(window.data() + 4), 4) == "TFL3") {
                
                std::uint32_t modelSize = 0;
                std::copy_n(window.data(), sizeof(std::uint32_t), reinterpret_cast<std::uint8_t*>(&modelSize));

                results.push_back(EmbeddedAsset{
                    .offset = static_cast<std::uint32_t>(i),
                    .size = modelSize,
                    .kind = AssetKind::TFLiteModel,
                    .identifier = "model-tflite-rom-0x" + toHex(static_cast<std::uint32_t>(i))
                });
                i += 512;
                continue;
            }
        }
        return results;
    }

private:
    static std::string toHex(std::uint32_t val) {
        char buf[16];
        std::snprintf(buf, sizeof(buf), "%08X", val);
        return std::string(buf);
    }
};
