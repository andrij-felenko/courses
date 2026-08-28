static gboolean
on_bus_message (GstBus *bus, GstMessage *msg, gpointer user_data)
{
  App *app = user_data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar *dbg = NULL;
      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("помилка від %s: %s\n", GST_OBJECT_NAME (msg->src), err->message);
      if (dbg)
        g_printerr ("  %s\n", dbg);
      g_clear_error (&err);
      g_free (dbg);
      g_main_loop_quit (app->loop);
      break;
    }
    case GST_MESSAGE_EOS:
      g_print ("кінець потоку\n");
      g_main_loop_quit (app->loop);
      break;
    default:
      break;
  }
  return TRUE;   /* лишити спостерігача на шині */
}
