// frame_loop.cpp — кадр із конвеєра → OpenCV → назад у конвеєр.

#include <gst/gst.h>
#include <gst/app/gstappsink.h>
#include <gst/app/gstappsrc.h>
#include <gst/video/video.h>

#include <opencv2/imgproc.hpp>

#include <csignal>
#include <cstdio>
#include <string>

static volatile sig_atomic_t g_stop = 0;
static void on_sigint (int) { g_stop = 1; }

/* Обробка. Малюємо ВЖЕ у власній пам'яті: frame — заголовок над
   вихідним буфером, який ми самі щойно виділили.
   putText уміє лише латиницю, тому напис англійський. */
static void process (cv::Mat &frame, guint64 n)
{
  cv::Mat gray;
  cv::cvtColor (frame, gray, cv::COLOR_BGR2GRAY);
  double lum = cv::mean (gray)[0];

  char label[64];
  std::snprintf (label, sizeof label, "frame %llu   mean %.1f",
                 (unsigned long long) n, lum);
  cv::rectangle (frame, cv::Rect (8, 8, 330, 34),
                 cv::Scalar (0, 0, 0), cv::FILLED);
  cv::putText (frame, label, cv::Point (16, 32), cv::FONT_HERSHEY_SIMPLEX,
               0.6, cv::Scalar (255, 255, 255), 1, cv::LINE_AA);
}

/* Помилку на шині забираємо НЕ блокуючись — інакше цикл кадрів стане. */
static bool bus_ok (GstElement *pipeline, const char *who)
{
  GstBus *bus = gst_element_get_bus (pipeline);
  GstMessage *msg = gst_bus_pop_filtered (bus, GST_MESSAGE_ERROR);
  bool ok = true;
  if (msg) {
    GError *e = NULL; gchar *dbg = NULL;
    gst_message_parse_error (msg, &e, &dbg);
    g_printerr ("[%s] %s (%s)\n", who, e->message, dbg ? dbg : "-");
    g_clear_error (&e); g_free (dbg);
    gst_message_unref (msg);
    ok = false;
  }
  gst_object_unref (bus);
  return ok;
}

/* Другий конвеєр будуємо ТІЛЬКИ тоді, коли з першого кадру відомі
   справжні роздільність і частота. */
static GstElement *build_output (GstVideoInfo *info, GstAppSrc **src_out)
{
  const char *desc =
      "appsrc name=in format=time ! videoconvert ! "
      "x264enc tune=zerolatency speed-preset=veryfast bitrate=4000 "
      "         key-int-max=30 ! "
      "h264parse ! mp4mux ! filesink location=out.mp4";

  GError *e = NULL;
  GstElement *p = gst_parse_launch (desc, &e);
  if (!p) { g_printerr ("вихід: %s\n", e->message); g_clear_error (&e); return NULL; }

  GstAppSrc *src = GST_APP_SRC (gst_bin_get_by_name (GST_BIN (p), "in"));

  /* Caps будуємо з того самого GstVideoInfo, з якого потім беремо
     розмір буфера й крок рядка — тож розійтися вони не можуть. */
  GstCaps *caps = gst_video_info_to_caps (info);
  gst_app_src_set_caps (src, caps);
  gst_caps_unref (caps);

  /* block=TRUE безпечний РІВНО ТОМУ, що штовхаємо зі свого потоку:
     тут блокування гальмує наш цикл, а не потік передавання камери. */
  g_object_set (src, "block", TRUE,
                "max-bytes", (guint64) (4 * GST_VIDEO_INFO_SIZE (info)), NULL);

  gst_element_set_state (p, GST_STATE_PLAYING);
  *src_out = src;
  return p;
}

int main (int argc, char *argv[])
{
  gst_init (&argc, &argv);
  std::signal (SIGINT, on_sigint);

  /* Фільтр caps після videoconvert — це замовлення формату: саме ним ми
     змушуємо конвеєр віддати BGR, якого чекає cv::Mat. decodebin віддає
     пад не одразу, але відкладене з'єднання gst_parse_launch ставить сам. */
  std::string in_desc = (argc > 1)
      ? std::string ("filesrc location=\"") + argv[1] + "\" ! decodebin ! "
        "videoconvert ! video/x-raw,format=BGR ! appsink name=out"
      : std::string ("v4l2src device=/dev/video0 ! videoconvert ! "
                     "video/x-raw,format=BGR ! appsink name=out");

  GError *e = NULL;
  GstElement *pin = gst_parse_launch (in_desc.c_str (), &e);
  if (!pin) { g_printerr ("вхід: %s\n", e->message); return 1; }

  GstAppSink *sink = GST_APP_SINK (gst_bin_get_by_name (GST_BIN (pin), "out"));
  g_object_set (sink,
                "sync",        FALSE,      /* кадр потрібен, щойно він є */
                "max-buffers", (guint) 2,  /* дві миті затримки, не більше */
                "drop",        TRUE,       /* з 1.28 — leaky-type=downstream */
                NULL);
  gst_element_set_state (pin, GST_STATE_PLAYING);

  GstElement   *pout   = NULL;
  GstAppSrc    *src    = NULL;
  GstCaps      *known  = NULL;              /* caps, під які зібрано вихід */
  GstVideoInfo  info;
  GstClockTime  base   = GST_CLOCK_TIME_NONE;   /* PTS першого кадру */
  guint64       frames = 0;

  while (!g_stop) {
    GstSample *sample = gst_app_sink_try_pull_sample (sink, 200 * GST_MSECOND);
    if (!sample) {                       /* таймаут, кінець або біда */
      if (gst_app_sink_is_eos (sink)) break;
      if (!bus_ok (pin, "вхід")) break;
      continue;
    }

    GstCaps *caps = gst_sample_get_caps (sample);   /* належить семплу */
    if (!known) {
      if (!gst_video_info_from_caps (&info, caps)) {
        g_printerr ("незрозумілі caps\n"); gst_sample_unref (sample); break;
      }
      known = gst_caps_ref (caps);
      pout  = build_output (&info, &src);
      if (!pout) { gst_sample_unref (sample); break; }
    } else if (!gst_caps_is_equal (caps, known)) {
      /* Формат змінився посеред потоку — камера перемкнула роздільність.
         Зупиняємось чесно: перебудова гілки кодування на льоту — окрема
         задача, а мовчки різати кадр під старий розмір не можна. */
      g_printerr ("формат змінився посеред потоку\n");
      gst_sample_unref (sample);
      break;
    }

    GstBuffer *inbuf = gst_sample_get_buffer (sample);   /* теж належить семплу */

    GstVideoFrame in_f;
    if (!gst_video_frame_map (&in_f, &info, inbuf, GST_MAP_READ)) {
      gst_sample_unref (sample);
      continue;
    }

    /* Заголовок поверх ЧУЖОЇ пам'яті — жодного скопійованого байта.
       П'ятий аргумент — КРОК РЯДКА; без нього OpenCV вважає рядок
       щільним і на вирівняному кадрі малює косі смуги. */
    cv::Mat view (GST_VIDEO_FRAME_HEIGHT (&in_f),
                  GST_VIDEO_FRAME_WIDTH  (&in_f), CV_8UC3,
                  GST_VIDEO_FRAME_PLANE_DATA   (&in_f, 0),
                  GST_VIDEO_FRAME_PLANE_STRIDE (&in_f, 0));

    /* Вихідний буфер — наш власний і писабельний. Розмір бере
       GstVideoInfo, тож кроки збігаються з тим, чого чекає кодер. */
    GstBuffer *outbuf =
        gst_buffer_new_allocate (NULL, GST_VIDEO_INFO_SIZE (&info), NULL);
    GstVideoFrame out_f;
    gst_video_frame_map (&out_f, &info, outbuf, GST_MAP_WRITE);
    cv::Mat dst (GST_VIDEO_FRAME_HEIGHT (&out_f),
                 GST_VIDEO_FRAME_WIDTH  (&out_f), CV_8UC3,
                 GST_VIDEO_FRAME_PLANE_DATA   (&out_f, 0),
                 GST_VIDEO_FRAME_PLANE_STRIDE (&out_f, 0));

    view.copyTo (dst);        /* ЄДИНА повна копія кадру в цьому циклі */
    process (dst, frames);    /* малюємо вже у своїй пам'яті */

    gst_video_frame_unmap (&out_f);
    gst_video_frame_unmap (&in_f);

    /* Час беремо з ВХІДНОГО кадру, а не з лічильника: якщо appsink щось
       викинув, справжні мітки збережуть реальний темп, а нумерація
       кадрів мовчки пришвидшила б запис. */
    GstClockTime pts = GST_BUFFER_PTS (inbuf);
    GstClockTime dur = GST_BUFFER_DURATION (inbuf);
    if (!GST_CLOCK_TIME_IS_VALID (dur))
      dur = (GST_VIDEO_INFO_FPS_N (&info) > 0)
          ? gst_util_uint64_scale_int (GST_SECOND,
                                       GST_VIDEO_INFO_FPS_D (&info),
                                       GST_VIDEO_INFO_FPS_N (&info))
          : 33 * GST_MSECOND;
    if (!GST_CLOCK_TIME_IS_VALID (pts))  pts  = frames * dur;
    if (!GST_CLOCK_TIME_IS_VALID (base)) base = pts;

    GST_BUFFER_PTS      (outbuf) = (pts > base) ? pts - base : 0;
    GST_BUFFER_DTS      (outbuf) = GST_CLOCK_TIME_NONE;   /* поставить кодер */
    GST_BUFFER_DURATION (outbuf) = dur;

    gst_sample_unref (sample);   /* пам'ять — назад у пул, якомога раніше */

    GstFlowReturn ret = gst_app_src_push_buffer (src, outbuf);
    if (ret != GST_FLOW_OK) {    /* outbuf уже НЕ наш — за будь-якого ret */
      g_printerr ("вихід зупинився: %s\n", gst_flow_get_name (ret));
      break;
    }
    if (!bus_ok (pout, "вихід")) break;
    ++frames;
  }

  /* Порядок згортання: перестати штовхати → EOS → ДОЧЕКАТИСЯ його на
     шині → лише тоді NULL. Без очікування mp4mux не допише moov. */
  if (src) {
    gst_app_src_end_of_stream (src);
    GstBus *bus = gst_element_get_bus (pout);
    GstMessage *msg = gst_bus_timed_pop_filtered (
        bus, 10 * GST_SECOND,
        (GstMessageType) (GST_MESSAGE_EOS | GST_MESSAGE_ERROR));
    if (!msg) g_printerr ("EOS не дійшов за 10 с — файл може бути битий\n");
    else      gst_message_unref (msg);
    gst_object_unref (bus);
  }

  gst_element_set_state (pin, GST_STATE_NULL);
  if (pout) gst_element_set_state (pout, GST_STATE_NULL);

  if (known) gst_caps_unref (known);
  if (src)   gst_object_unref (src);
  if (pout)  gst_object_unref (pout);
  gst_object_unref (sink);
  gst_object_unref (pin);

  g_printerr ("кадрів: %" G_GUINT64_FORMAT "\n", frames);
  return 0;
}
