static gboolean
prepare_pipeline (App * app)
{
  GError *err = NULL;
  GstElement *probe;
  GstBus *bus;

  app->pipeline = gst_parse_launch (PIPELINE_DESC, &err);
  if (!app->pipeline) {
    g_printerr ("конвеєр не зібрався: %s\n", err->message);
    g_clear_error (&err);
    return FALSE;
  }

  /* 1. Годинник наш — конвеєрові нема чого вибирати й нема що втрачати. */
  gst_pipeline_use_clock (GST_PIPELINE (app->pipeline), app->clock);

  /* 2. base_time теж наш: зі start_time = NONE конвеєр більше
   *    НЕ перепризначає його на жодному переході станів.          */
  gst_pipeline_set_start_time (GST_PIPELINE (app->pipeline), GST_CLOCK_TIME_NONE);

  /* 3. Однакова затримка на всіх машинах, хоч би які там споживачі. */
  gst_pipeline_set_latency (GST_PIPELINE (app->pipeline), 100 * GST_MSECOND);

  probe = gst_bin_get_by_name (GST_BIN (app->pipeline), "probe");
  if (probe) {
    g_signal_connect (probe, "handoff", G_CALLBACK (on_frame_rendered), app);
    gst_object_unref (probe);
  }

  bus = gst_element_get_bus (app->pipeline);
  gst_bus_add_watch (bus, on_bus, app);
  if (GST_IS_NET_CLIENT_CLOCK (app->clock))
    g_object_set (app->clock, "bus", bus, NULL);   /* статистика — у ту саму шину */
  gst_object_unref (bus);

  /* Прерол: декодер, вікно й буфери мають бути готові ДО того, як настане T,
     інакше перший кадр вийде із запізненням на власний розігрів конвеєра. */
  if (gst_element_set_state (app->pipeline, GST_STATE_PAUSED) == GST_STATE_CHANGE_FAILURE)
    return FALSE;
  gst_element_get_state (app->pipeline, NULL, NULL, 10 * GST_SECOND);

  return TRUE;
}

static void
start_at (App * app, GstClockTime base_time)
{
  gst_element_set_base_time (app->pipeline, base_time);
  gst_element_set_state (app->pipeline, GST_STATE_PLAYING);

  g_print ("base_time = %" G_GUINT64_FORMAT " нс, зараз %" G_GUINT64_FORMAT " нс\n",
           base_time, gst_clock_get_time (app->clock));
}
