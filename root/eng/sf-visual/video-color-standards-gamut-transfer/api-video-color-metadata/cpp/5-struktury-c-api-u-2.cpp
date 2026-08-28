// cpp
#include <memory>
#include <stdexcept>
extern "C" {
#include <libswscale/swscale.h>
#include <libavutil/frame.h>
}

namespace media {

struct SwsDeleter {
    void operator()(SwsContext* ptr) const noexcept {
        if (ptr) sws_freeContext(ptr);
    }
};

using UniqueSwsContext = std::unique_ptr<SwsContext, SwsDeleter>;

/**
 * Ідіоматична C++ обгортка над SwsContext з автоматичним керуванням ресурсами (RAII)
 */
class ColorScalePipeline {
public:
    ColorScalePipeline(const AVFrame& src_frame, int dst_width, int dst_height, AVPixelFormat dst_format) {
        SwsContext* ctx = sws_getContext(
            src_frame.width, src_frame.height, src_frame.format,
            dst_width, dst_height, dst_format,
            SWS_BILINEAR, nullptr, nullptr, nullptr
        );

        if (!ctx) {
            throw std::runtime_error("Не вдалося створити SwsContext для колірного перетворення");
        }

        ctx_.reset(ctx);
        configure_color_spaces(src_frame);
    }

    SwsContext* get() const noexcept { return ctx_.get(); }

private:
    void configure_color_spaces(const AVFrame& src_frame) {
        int src_cs = (src_frame.colorspace == AVCOL_SPC_BT2020_NCL) ? SWS_CS_BT2020 : SWS_CS_ITU709;
        int dst_cs = SWS_CS_DEFAULT;

        int src_range = (src_frame.color_range == AVCOL_RANGE_JPEG) ? 1 : 0;
        int dst_range = 1;

        const int *inv_table = sws_getCoefficients(src_cs);
        const int *table = sws_getCoefficients(dst_cs);

        int dummy_src_full, dummy_dst_full;
        int brightness, contrast, saturation;

        sws_getColorspaceDetails(ctx_.get(), const_cast<int**>(&inv_table), &dummy_src_full,
                                 const_cast<int**>(&table), &dummy_dst_full,
                                 &brightness, &contrast, &saturation);

        sws_setColorspaceDetails(ctx_.get(), inv_table, src_range,
                                 table, dst_range,
                                 brightness, contrast, saturation);
    }

    UniqueSwsContext ctx_;
};

} // namespace media
