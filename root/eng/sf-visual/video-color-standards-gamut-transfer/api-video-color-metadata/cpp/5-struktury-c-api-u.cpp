// cpp
extern "C" {
#include <libavutil/frame.h>
#include <libavutil/pixfmt.h>
}

// У C++20 метадані колірності AVFrame доступні через прямий доступ до полів структури
struct FrameColorMetadata {
    AVColorRange range{AVCOL_RANGE_MPEG};
    AVColorPrimaries primaries{AVCOL_PRI_BT709};
    AVColorTransferCharacteristic trc{AVCOL_TRC_BT709};
    AVColorSpace space{AVCOL_SPC_BT709};

    static FrameColorMetadata extract(const AVFrame& frame) noexcept {
        return FrameColorMetadata{
            .range = frame.color_range,
            .primaries = frame.color_primaries,
            .trc = frame.color_trc,
            .space = frame.colorspace
        };
    }
};
