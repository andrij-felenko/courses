#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <cmath>
#include <array>
#include <optional>
#include <algorithm>

enum class AssetType {
    Unknown,
    FontTrueType,
    TFLiteModel,
    HighEntropyBlob
};

struct AssetDescriptor {
    std::size_t offset{0};
    std::size_t size{0};
    AssetType type{AssetType::Unknown};
    double entropy{0.0};
    std::array<uint8_t, 32> sha256{};
};

class FirmwareAssetScanner {
public:
    static double calculateEntropy(std::span<const uint8_t> data) noexcept {
        if (data.empty()) return 0.0;
        std::array<std::size_t, 256> counts{};
        for (const uint8_t byte : data) {
            counts[byte]++;
        }
        double entropy = 0.0;
        const double total = static_cast<double>(data.size());
        for (const std::size_t count : counts) {
            if (count > 0) {
                const double p = static_cast<double>(count) / total;
                entropy -= p * std::log2(p);
            }
        }
        return entropy;
    }

    static std::vector<AssetDescriptor> scan(std::span<const uint8_t> firmware) {
        std::vector<AssetDescriptor> detected;
        if (firmware.size() < 16) return detected;

        for (std::size_t i = 0; i + 16 < firmware.size(); ++i) {
            const auto window = firmware.subspan(i);

            // Перевірка магічних чисел TrueType / OpenType
            const bool isTtf = (window[0] == 0x00 && window[1] == 0x01 && window[2] == 0x00 && window[3] == 0x00) ||
                               (std::string_view(reinterpret_cast<const char*>(window.data()), 4) == "OTTO") ||
                               (std::string_view(reinterpret_cast<const char*>(window.data()), 4) == "ttcf");

            if (isTtf) {
                const auto sampleSize = std::min<std::size_t>(window.size(), 1024);
                detected.push_back(AssetDescriptor{
                    .offset = i,
                    .size = 4096,
                    .type = AssetType::FontTrueType,
                    .entropy = calculateEntropy(window.subspan(0, sampleSize))
                });
                i += 256;
                continue;
            }

            // Перевірка магічного тегу TFLite FlatBuffers
            if (window.size() >= 8 &&
                std::string_view(reinterpret_cast<const char*>(window.data() + 4), 4) == "TFL3") {
                
                uint32_t modelSize = 0;
                std::copy_n(window.data(), sizeof(uint32_t), reinterpret_cast<uint8_t*>(&modelSize));
                const auto sampleSize = std::min<std::size_t>(window.size(), 1024);

                detected.push_back(AssetDescriptor{
                    .offset = i,
                    .size = modelSize > 0 ? modelSize : 8192,
                    .type = AssetType::TFLiteModel,
                    .entropy = calculateEntropy(window.subspan(0, sampleSize))
                });
                i += 512;
                continue;
            }
        }
        return detected;
    }
};
