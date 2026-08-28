static void
on_frame_rendered (GstElement * sink, GstBuffer * buf, GstPad * pad, gpointer data)
{
  App *app = data;
  static guint n = 0;

  if (n++ % 60)                      /* один рядок на секунду при 60 к/с */
    return;

  GstClockTime now  = gst_clock_get_time (app->clock);
  GstClockTime base = gst_element_get_base_time (sink);

  g_print ("PTS %" GST_TIME_FORMAT "  показано о %" G_GUINT64_FORMAT
           " нс  (running %" GST_TIME_FORMAT ")\n",
           GST_TIME_ARGS (GST_BUFFER_PTS (buf)), now, GST_TIME_ARGS (now - base));
}
