/* bridge.cpp — NV12 з апаратного декодера → cv::Mat → BGR назад у конвеєр.
 *
 *   g++ -O2 -std=c++17 bridge.cpp -o bridge \
 *       $(pkg-config --cflags --libs gstreamer-1.0 gstreamer-app-1.0 \
 *                                    gstreamer-video-1.0 opencv4)
 */
#include <gst/gst.h>
#include <gst/app/gstappsink.h>
#include <gst/app/gstappsrc.h>
#include <gst/video/video.h>
#include <opencv2/imgproc.hpp>
#include <vector>

struct Bridge {
  GstElement   *pipeline  = nullptr;
  GstElement   *sink      = nullptr;
  GstElement   *src       = nullptr;
  GstCaps      *in_caps   = nullptr;   /* caps, під які розібрано in_info */
  GstVideoInfo  in_info   {};
  bool          out_ready = false;
};

/* Ваша робота. Усе, що вміє працювати по яскравості, працює прямо тут. */
static void detect (const cv::Mat &luma, std::vector<cv::Rect> &out);

static GstFlowReturn on_new_sample (GstAppSink *sink, gpointer user_data);

int main (int argc, char *argv[])
{
  gst_init (&argc, &argv);
  Bridge b;

  /* NV12 — це ВИМОГА до декодера, а не сподівання. Один рядок caps
     робить те, чого не зробить жодне перетворення в нашому коді. */
  const char *desc =
      "rtspsrc location=rtsp://cam/stream latency=100 ! rtph264depay ! h264parse ! "
      "vaapih264dec ! video/x-raw,format=NV12 ! "
      "appsink name=cvsink sync=false max-buffers=2 drop=true "

      "appsrc name=cvsrc format=time is-live=true do-timestamp=false ! "
      "videoconvert ! x264enc tune=zerolatency speed-preset=veryfast ! "
      "h264parse ! matroskamux ! filesink location=out.mkv";

  GError *e = nullptr;
  b.pipeline = gst_parse_launch (desc, &e);
  if (!b.pipeline) { g_printerr ("конвеєр: %s\n", e->message); return 1; }

  b.sink = gst_bin_get_by_name (GST_BIN (b.pipeline), "cvsink");
  b.src  = gst_bin_get_by_name (GST_BIN (b.pipeline), "cvsrc");

  /* Вміст структури appsink копіює собі; static — просто страховка.
     Зворотний виклик отримає &b, а b живе до кінця main. */
  static GstAppSinkCallbacks cbs = {};
  cbs.new_sample = on_new_sample;
  gst_app_sink_set_callbacks (GST_APP_SINK (b.sink), &cbs, &b, nullptr);

  gst_element_set_state (b.pipeline, GST_STATE_PLAYING);

  GstBus     *bus = gst_element_get_bus (b.pipeline);
  GstMessage *msg = gst_bus_timed_pop_filtered (
      bus, GST_CLOCK_TIME_NONE,
      (GstMessageType) (GST_MESSAGE_ERROR | GST_MESSAGE_EOS));
  if (msg) gst_message_unref (msg);
  gst_object_unref (bus);

  /* Спершу NULL: доки конвеєр живий, у ньому можуть їхати наші буфери. */
  gst_element_set_state (b.pipeline, GST_STATE_NULL);
  gst_caps_replace (&b.in_caps, nullptr);
  gst_object_unref (b.sink);
  gst_object_unref (b.src);
  gst_object_unref (b.pipeline);
  return 0;
}
