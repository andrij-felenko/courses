// proprietary_engine.cpp — Закритий модуль обробки сигналів
#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <expected>

// Експортований C-інтерфейс зовнішньої LGPL-бібліотеки
extern "C" int lgpl_codec_compress(const uint8_t *in, size_t in_len, 
                                  uint8_t *out, size_t *out_len);

namespace proprietary {

namespace {
// Внутрішній пропрієтарний алгоритм у безназванному просторі імен
constexpr uint32_t math_filter(uint32_t raw_val) noexcept {
    uint32_t acc = raw_val * 0x45D9F3B;
    acc ^= (acc >> 16);
    return acc + 0x1234567;
}
} // namespace

enum class EngineError {
    InvalidInput,
    CompressionFailed
};

// Публічний C++ клас обробника
class [[gnu::visibility("default")]] SensorProcessor {
public:
    std::expected<size_t, EngineError> process(std::span<const uint8_t> input, 
                                               std::span<uint8_t> output) {
        if (input.empty() || output.empty()) {
            return std::unexpected(EngineError::InvalidInput);
        }

        std::vector<uint8_t> preprocessed;
        preprocessed.reserve(input.size());
        for (uint8_t b : input) {
            preprocessed.push_back(static_cast<uint8_t>(math_filter(b)));
        }

        size_t out_written = output.size();
        int rc = lgpl_codec_compress(preprocessed.data(), preprocessed.size(), 
                                     output.data(), &out_written);
        if (rc != 0) {
            return std::unexpected(EngineError::CompressionFailed);
        }

        return out_written;
    }
};

} // namespace proprietary

// Зовнішня C-обгортка для лінкування точки входу
extern "C" [[gnu::visibility("default")]]
int process_sensor_stream(const uint8_t *raw_buf, size_t len, 
                          uint8_t *out_buf, size_t *out_len) {
    if (!raw_buf || !out_buf || !out_len) return -1;
    
    proprietary::SensorProcessor proc;
    auto res = proc.process(std::span(raw_buf, len), std::span(out_buf, *out_len));
    if (!res) return -1;
    
    *out_len = *res;
    return 0;
}
