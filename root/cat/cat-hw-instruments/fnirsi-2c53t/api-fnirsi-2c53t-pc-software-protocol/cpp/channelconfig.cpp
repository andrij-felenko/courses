#include <cstdint>
#include <vector>

struct ChannelConfig {
    float v_scale;   // Ціна розряду АЦП у вольтах
    float v_offset;  // Зміщення осі у вольтах
    uint8_t d_zero;  // Значення нуля АЦП (128)
};

class WaveformDecoder {
public:
    static std::vector<float> decode(const std::vector<uint8_t>& raw_bytes, const ChannelConfig& cfg) {
        std::vector<float> voltages(raw_bytes.size());
        for (size_t i = 0; i < raw_bytes.size(); ++i) {
            voltages[i] = (static_cast<float>(raw_bytes[i]) - static_cast<float>(cfg.d_zero)) * cfg.v_scale - cfg.v_offset;
        }
        return voltages;
    }
};
