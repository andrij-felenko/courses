static gboolean on_bus_message (GstBus *bus, GstMessage *msg, gpointer user_data)
{
  GMainLoop *loop = user_data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar *dbg = NULL;
      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("помилка від %s: %s\n", GST_OBJECT_NAME (msg->src), err->message);
      g_printerr ("подробиці: %s\n", dbg ? dbg : "(немає)");
      g_clear_error (&err);
      g_free (dbg);
      g_main_loop_quit (loop);
      break;
    }
    case GST_MESSAGE_EOS:
      g_print ("потік скінчився\n");
      g_main_loop_quit (loop);
      break;
    default:
      break;
  }
  return TRUE;                    /* лишаємося підключеними */
}

/* ... */
GstBus *bus = gst_element_get_bus (pipeline);
gst_bus_add_watch (bus, on_bus_message, loop);
gst_object_unref (bus);
