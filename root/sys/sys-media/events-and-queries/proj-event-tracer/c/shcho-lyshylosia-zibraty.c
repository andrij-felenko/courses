static gboolean
on_bus (GstBus *bus, GstMessage *msg, gpointer data)
{
  if (GST_MESSAGE_TYPE (msg) & (GST_MESSAGE_EOS | GST_MESSAGE_ERROR))
    g_main_loop_quit (data);
  return TRUE;
}

int
main (int argc, char *argv[])
{
  GstElement *pipeline, *src, *queue, *sink;
  GstCaps *caps;
  GstPad *qsrc;
  GMainLoop *loop;
  GstBus *bus;

  gst_init (&argc, &argv);
  t_start = g_get_monotonic_time ();
  g_mutex_init (&names_lock);
  names = g_hash_table_new (NULL, NULL);

  pipeline = gst_pipeline_new ("tracer");
  src   = gst_element_factory_make ("videotestsrc", NULL);
  queue = gst_element_factory_make ("queue", NULL);
  sink  = gst_element_factory_make ("fakesink", NULL);
  g_assert (src != NULL && queue != NULL && sink != NULL);

  g_object_set (src, "num-buffers", 150, NULL);
  g_object_set (queue, "max-size-time", (guint64) (200 * GST_MSECOND),
                       "max-size-buffers", (guint) 0,
                       "max-size-bytes", (guint) 0, NULL);
  g_object_set (sink, "sync", TRUE, NULL);

  gst_bin_add_many (GST_BIN (pipeline), src, queue, sink, NULL);
  caps = gst_caps_from_string ("video/x-raw,width=320,height=240,framerate=30/1");
  if (!gst_element_link_filtered (src, queue, caps) ||
      !gst_element_link (queue, sink))
    g_error ("конвеєр не зв'язався");
  gst_caps_unref (caps);              /* фільтр передано БЕЗ володіння */

  watch (queue, "sink", "queue.sink");
  watch (queue, "src",  "queue.src");
  qsrc = gst_element_get_static_pad (queue, "src");

  loop = g_main_loop_new (NULL, FALSE);
  bus = gst_element_get_bus (pipeline);
  gst_bus_add_watch (bus, on_bus, loop);
  gst_object_unref (bus);

  gst_element_set_state (pipeline, GST_STATE_PLAYING);
  g_timeout_add (1500, send_marks, pipeline);      /* черга вже повна */
  g_timeout_add (2500, duration_demo, qsrc);
  g_main_loop_run (loop);

  gst_element_set_state (pipeline, GST_STATE_NULL);
  gst_object_unref (qsrc);
  gst_object_unref (pipeline);
  g_main_loop_unref (loop);
  return 0;
}
