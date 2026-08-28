/* udpsrc timeout=2000000000  →  повідомлення на шину після 2 с тиші */
static gboolean
on_bus (GstBus * bus, GstMessage * msg, gpointer user_data)
{
  const GstStructure *s = gst_message_get_structure (msg);

  if (GST_MESSAGE_TYPE (msg) == GST_MESSAGE_ELEMENT &&
      s && gst_structure_has_name (s, "GstUDPSrcTimeout")) {
    guint64 ns = 0;
    gst_structure_get_uint64 (s, "timeout", &ns);
    g_printerr ("тиша в сокеті довша за %" G_GUINT64_FORMAT " нс\n", ns);
  }
  return TRUE;                  /* повідомлення не «спожите» — хай іде далі */
}
