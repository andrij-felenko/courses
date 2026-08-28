/* dynlink.c — гілки, що чіпляються до qtdemux під час роботи.
 *   зібрати:   gcc dynlink.c -o dynlink $(pkg-config --cflags --libs gstreamer-1.0)
 *   запустити: ./dynlink кіно.mp4 5     (через 5 с відрізати відеогілку)
 */
#include <gst/gst.h>
#include <stdlib.h>

typedef struct {
  GstElement *pipeline;
  GMainLoop  *loop;

  GstElement *video_branch;   /* бін гілки, доки вона в конвеєрі */
  GstElement *audio_branch;
  GstElement *video_tail;     /* останній елемент відеогілки — треба лише для дренажу */
  GstPad     *video_pad;      /* src-пад qtdemux, з якого живе відеогілка */
  gint        cut_started;    /* одноразовий засув для розрізу */
} App;

static const gchar *const VIDEO_BRANCH[] = {
  "queue", "h264parse", "avdec_h264", "videoconvert", "autovideosink", NULL
};
static const gchar *const AUDIO_BRANCH[] = {
  "queue", "aacparse", "avdec_aac", "audioconvert", "audioresample",
  "autoaudiosink", NULL
};

/* оголошення наперед — тіла нижче */
static void     on_pad_added     (GstElement *demux, GstPad *newpad, gpointer user_data);
static gboolean on_bus_message   (GstBus *bus, GstMessage *msg, gpointer user_data);
static gboolean cut_video_branch (gpointer user_data);

int
main (int argc, char *argv[])
{
  App app = { 0 };

  gst_init (&argc, &argv);
  if (argc < 2) {
    g_printerr ("вжиток: %s файл.mp4 [секунд до відрізання відеогілки]\n", argv[0]);
    return 1;
  }

  app.loop = g_main_loop_new (NULL, FALSE);
  app.pipeline = gst_pipeline_new ("dyn");

  GstElement *src   = gst_element_factory_make ("filesrc", NULL);
  GstElement *demux = gst_element_factory_make ("qtdemux", NULL);
  g_object_set (src, "location", argv[1], NULL);

  gst_bin_add_many (GST_BIN (app.pipeline), src, demux, NULL);
  if (!gst_element_link (src, demux))
    g_error ("filesrc → qtdemux не з'єдналися");

  /* Усе, що нижче qtdemux, з'явиться потім. Єдине, що можна зробити зараз, —
     сказати, кого кликати, коли воно з'явиться. */
  g_signal_connect (demux, "pad-added", G_CALLBACK (on_pad_added), &app);

  GstBus *bus = gst_element_get_bus (app.pipeline);
  gst_bus_add_watch (bus, on_bus_message, &app);
  gst_object_unref (bus);

  gst_element_set_state (app.pipeline, GST_STATE_PLAYING);
  if (argc > 2)
    g_timeout_add_seconds ((guint) atoi (argv[2]), cut_video_branch, &app);

  g_main_loop_run (app.loop);

  gst_element_set_state (app.pipeline, GST_STATE_NULL);
  gst_object_unref (app.pipeline);
  g_main_loop_unref (app.loop);
  return 0;
}
