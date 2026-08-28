// gst_mat_inplace.cpp — кадр із appsink у cv::Mat, обробка на місці,
// той самий буфер далі в конвеєр.
//
//   g++ -O2 -std=c++17 gst_mat_inplace.cpp -o gst_mat_inplace \
//       $(pkg-config --cflags --libs gstreamer-1.0 gstreamer-app-1.0 \
//                                    gstreamer-video-1.0 opencv4)

#include <gst/gst.h>
#include <gst/app/gstappsink.h>
#include <gst/app/gstappsrc.h>
#include <gst/video/video.h>

#include <opencv2/imgproc.hpp>

#include <csignal>

static volatile sig_atomic_t g_stop = 0;
static void on_sigint (int) { g_stop = 1; }

/* Відображення, прив'язане до області видимості: unmap станеться сам —
   і на ранньому return, і на винятку з надр OpenCV. */
class MappedFrame {
public:
  MappedFrame (const GstVideoInfo *info, GstBuffer *buf, GstMapFlags flags)
      : ok_ (gst_video_frame_map (&f_, info, buf, flags)) {}

  ~MappedFrame () { if (ok_) gst_video_frame_unmap (&f_); }

  MappedFrame (const MappedFrame &)            = delete;   /* копії заборонені: */
  MappedFrame &operator= (const MappedFrame &) = delete;   /* unmap рівно один  */

  explicit operator bool () const { return ok_; }

  int width  () const { return GST_VIDEO_FRAME_WIDTH  (&f_); }
  int height () const { return GST_VIDEO_FRAME_HEIGHT (&f_); }

  const GstVideoFrame *get () const { return &f_; }   /* для решти макросів */

  /* Заголовок над площиною p. Розмір і тип задає викликач — лише він знає,
     про який формат домовився конвеєр. Крок береться з КАДРУ. */
  cv::Mat plane (guint p, int rows, int cols, int cvType) const
  {
    return cv::Mat (rows, cols, cvType,
                    GST_VIDEO_FRAME_PLANE_DATA (&f_, p),
                    (size_t) GST_VIDEO_FRAME_PLANE_STRIDE (&f_, p));
  }

private:
  GstVideoFrame f_ {};    /* оголошений ПЕРШИМ: map у списку ініціалізації */
  gboolean      ok_;      /* працює вже над готовим полем                  */
};
