static void
do_seek (GstElement *pipeline, gpointer user_data)
{
  gint64 pos = *(gint64 *) user_data;

  gst_element_seek_simple (pipeline, GST_FORMAT_TIME,
                           GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_KEY_UNIT, pos);
}

/* із зонда на паді, тобто з потоку конвеєра: */
gint64 *pos_copy = g_new (gint64, 1);

*pos_copy = 12.5 * GST_SECOND;
gst_element_call_async (pipeline, do_seek, pos_copy, g_free);
