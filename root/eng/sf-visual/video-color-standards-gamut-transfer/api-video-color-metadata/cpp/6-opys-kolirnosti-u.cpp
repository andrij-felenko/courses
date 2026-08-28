// cpp
#include <gst/video/video-color.h>
#include <string_view>
#include <optional>

namespace gst {

std::optional<GstVideoColorimetry> parse_colorimetry(std::string_view colorimetry_str) {
    GstVideoColorimetry colorimetry{};
    if (gst_video_colorimetry_from_string(&colorimetry, colorimetry_str.data())) {
        return colorimetry;
    }
    return std::nullopt;
}

} // namespace gst
