static gboolean
select_stream (GstElement * src, guint num, GstCaps * caps, gpointer user_data)
{
  const GstStructure *s = gst_caps_get_structure (caps, 0);

  /* FALSE тут означає «не робити SETUP», а не «прийняти й викинути» */
  return g_strcmp0 (gst_structure_get_string (s, "media"), "video") == 0;
}

static void
on_pad_added (GstElement * src, GstPad * pad, gpointer depay)
{
  GstPad *sink = gst_element_get_static_pad (GST_ELEMENT (depay), "sink");

  if (!gst_pad_is_linked (sink))
    gst_pad_link (pad, sink);
  gst_object_unref (sink);
}

g_signal_connect (rtspsrc, "select-stream", G_CALLBACK (select_stream), NULL);
g_signal_connect (rtspsrc, "pad-added", G_CALLBACK (on_pad_added), depay);
