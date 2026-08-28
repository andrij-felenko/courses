// gstcvbridge.hpp — спільне для всіх трьох версій
#include <gst/gst.h>
#include <gst/app/gstappsink.h>
#include <gst/video/video.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <memory>

// Формати, які лягають у cv::Mat без жодного перетворення.
static int cvTypeForVideo(GstVideoFormat fmt)
{
    switch (fmt) {
        case GST_VIDEO_FORMAT_BGR:       return CV_8UC3;
        case GST_VIDEO_FORMAT_RGB:       return CV_8UC3;  // ⚠ канали переставлені
        case GST_VIDEO_FORMAT_BGRA:
        case GST_VIDEO_FORMAT_BGRx:      return CV_8UC4;
        case GST_VIDEO_FORMAT_GRAY8:     return CV_8UC1;
        case GST_VIDEO_FORMAT_GRAY16_LE: return CV_16UC1;
        default:                         return -1;       // NV12, I420, YUY2 — окрема розмова
    }
}

struct FrameFormat {
    GstVideoInfo info;
    GstCaps*     caps   = nullptr;   // caps, для яких пораховано info
    int          cvType = -1;

    FrameFormat()  { gst_video_info_init(&info); }
    ~FrameFormat() { gst_caps_replace(&caps, nullptr); }
};

// Розбирає caps лише тоді, коли вони справді змінилися.
static bool refreshFormat(FrameFormat& ff, GstCaps* caps)
{
    if (ff.caps && gst_caps_is_equal(caps, ff.caps))
        return ff.cvType >= 0;
    if (!gst_video_info_from_caps(&ff.info, caps))
        return false;
    ff.cvType = cvTypeForVideo(GST_VIDEO_INFO_FORMAT(&ff.info));
    gst_caps_replace(&ff.caps, caps);   // тепер тримаємо власне посилання
    return ff.cvType >= 0;
}
