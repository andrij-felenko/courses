static void
watch (GstElement *elem, const gchar *padname, const gchar *tag)
{
  GstPad *pad = gst_element_get_static_pad (elem, padname);
  Point *p = g_new0 (Point, 1);

  p->tag = tag;
  gst_pad_add_probe (pad,
      GST_PAD_PROBE_TYPE_BUFFER | GST_PAD_PROBE_TYPE_BUFFER_LIST |
      GST_PAD_PROBE_TYPE_EVENT_BOTH | GST_PAD_PROBE_TYPE_EVENT_FLUSH |
      GST_PAD_PROBE_TYPE_QUERY_BOTH,
      trace_cb, p, g_free);           /* g_free звільнить Point разом із зондом */
  gst_object_unref (pad);
}
