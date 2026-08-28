static GstEvent *
mark (GstEventType type)
{
  return gst_event_new_custom (type,
      gst_structure_new ("tracer-mark", "sent-ms", G_TYPE_INT64, ms_now (), NULL));
}

static gboolean
send_marks (gpointer data)
{
  GstElement *pipeline = data;

  g_print ("\n--- %" G_GINT64_FORMAT " мс: шлемо дві власні події поспіль ---\n",
           ms_now ());
  gst_element_send_event (pipeline, mark (GST_EVENT_CUSTOM_DOWNSTREAM));
  gst_element_send_event (pipeline, mark (GST_EVENT_CUSTOM_DOWNSTREAM_OOB));
  return G_SOURCE_REMOVE;
}
