#include <gst/gst.h>

static GstPadProbeReturn
on_buffer (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  guint *n = user_data;
  GstBuffer *buf = gst_pad_probe_info_get_buffer (info);   /* позичене */

  if (buf != NULL) {
    (*n)++;
    g_print ("буфер %2u  pts %" GST_TIME_FORMAT "\n",
             *n, GST_TIME_ARGS (GST_BUFFER_PTS (buf)));
  }
  return GST_PAD_PROBE_OK;                  /* пропустити далі, пробу лишити */
}

int
main (int argc, char **argv)
{
  guint n = 0;

  gst_init (&argc, &argv);

  GstElement *pipe = gst_pipeline_new ("p");
  GstElement *src  = gst_element_factory_make ("videotestsrc", NULL);
  GstElement *conv = gst_element_factory_make ("videoconvert", NULL);
  GstElement *sink = gst_element_factory_make ("fakesink", NULL);

  g_object_set (src, "num-buffers", 10, NULL);

  /* спершу в бін — інакше буде GST_PAD_LINK_WRONG_HIERARCHY */
  gst_bin_add_many (GST_BIN (pipe), src, conv, sink, NULL);

  GstPad *srcpad  = gst_element_get_static_pad (src,  "src");    /* +1 */
  GstPad *sinkpad = gst_element_get_static_pad (conv, "sink");   /* +1 */

  GstPadLinkReturn lr = gst_pad_link (srcpad, sinkpad);
  if (GST_PAD_LINK_FAILED (lr)) {
    g_printerr ("не з'єдналося: %s\n", gst_pad_link_get_name (lr));
    return 1;
  }
  gst_object_unref (sinkpad);            /* більше не потрібен — віддаємо */

  /* обгортка: зручно, але причини невдачі не скаже */
  if (!gst_element_link (conv, sink))
    g_printerr ("videoconvert ! fakesink: не з'єдналося\n");

  gulong probe_id = gst_pad_add_probe (srcpad, GST_PAD_PROBE_TYPE_BUFFER,
                                       on_buffer, &n, NULL);

  gst_element_set_state (pipe, GST_STATE_PLAYING);

  GstBus *bus = gst_element_get_bus (pipe);
  GstMessage *msg = gst_bus_timed_pop_filtered (bus, GST_CLOCK_TIME_NONE,
      GST_MESSAGE_EOS | GST_MESSAGE_ERROR);

  if (msg != NULL && GST_MESSAGE_TYPE (msg) == GST_MESSAGE_ERROR) {
    GError *err = NULL;
    gst_message_parse_error (msg, &err, NULL);
    g_printerr ("помилка: %s\n", err->message);
    g_clear_error (&err);
  }

  gst_pad_remove_probe (srcpad, probe_id);
  gst_element_set_state (pipe, GST_STATE_NULL);

  if (msg != NULL)
    gst_message_unref (msg);
  gst_object_unref (bus);
  gst_object_unref (srcpad);             /* наше посилання з get_static_pad */
  gst_object_unref (pipe);
  return 0;
}
