// cpp
#include <cstdint>

namespace h264 {

struct VUIParameters {
    bool aspect_ratio_info_present{false};
    uint8_t aspect_ratio_idc{0};
    uint16_t sar_width{0};
    uint16_t sar_height{0};
    bool overscan_info_present{false};
    bool video_signal_type_present{false};
    uint8_t video_format{0};
    bool video_full_range{false};
    bool colour_description_present{false};
    uint8_t colour_primaries{2};
    uint8_t transfer_characteristics{2};
    uint8_t matrix_coefficients{2};
};

class BitStreamReader;

VUIParameters parse_vui_parameters_cpp(BitStreamReader& reader) {
    VUIParameters vui;
    vui.aspect_ratio_info_present = (reader.read_bits(1) != 0);
    if (vui.aspect_ratio_info_present) {
        vui.aspect_ratio_idc = static_cast<uint8_t>(reader.read_bits(8));
        if (vui.aspect_ratio_idc == 255 /* Extended_SAR */) {
            vui.sar_width  = static_cast<uint16_t>(reader.read_bits(16));
            vui.sar_height = static_cast<uint16_t>(reader.read_bits(16));
        }
    }
    vui.overscan_info_present = (reader.read_bits(1) != 0);
    vui.video_signal_type_present = (reader.read_bits(1) != 0);
    if (vui.video_signal_type_present) {
        vui.video_format = static_cast<uint8_t>(reader.read_bits(3));
        vui.video_full_range = (reader.read_bits(1) != 0);
        vui.colour_description_present = (reader.read_bits(1) != 0);
        if (vui.colour_description_present) {
            vui.colour_primaries         = static_cast<uint8_t>(reader.read_bits(8));
            vui.transfer_characteristics = static_cast<uint8_t>(reader.read_bits(8));
            vui.matrix_coefficients      = static_cast<uint8_t>(reader.read_bits(8));
        }
    }
    return vui;
}

} // namespace h264
