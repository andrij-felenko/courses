#include <cstdint>
#include <cstddef>

class Ov3640Diagnostic {
public:
    enum class FrameState {
        Ok,
        MissingSoi,
        MissingEoi,
        BufferOverflow
    };

    struct AnalysisResult {
        FrameState state;
        size_t frameSize;
    };

    static AnalysisResult analyzeJpegStream(const uint8_t* data, size_t length) {
        if (length < 4 || data[0] != 0xFF || data[1] != 0xD8) {
            return {FrameState::MissingSoi, 0};
        }

        for (size_t i = 2; i < length - 1; ++i) {
            if (data[i] == 0xFF && data[i + 1] == 0xD9) {
                return {FrameState::Ok, i + 2};
            }
        }

        return {FrameState::MissingEoi, length};
    }
};
