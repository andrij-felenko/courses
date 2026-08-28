static gboolean
on_bus (GstBus * bus, GstMessage * msg, gpointer data)
{
  App *app = data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ERROR:{
      GError *err = NULL;
      gchar *dbg = NULL;
      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("ПОМИЛКА від %s: %s\n", GST_OBJECT_NAME (msg->src), err->message);
      g_error_free (err);
      g_free (dbg);
      g_main_loop_quit (app->loop);
      break;
    }
    case GST_MESSAGE_EOS:
      g_main_loop_quit (app->loop);
      break;
    case GST_MESSAGE_ELEMENT:{
      const GstStructure *s = gst_message_get_structure (msg);
      guint64 rtt_avg = 0;
      gdouble r2 = 0;

      if (s && gst_structure_has_name (s, "gst-netclock-statistics") &&
          gst_structure_get (s, "rtt-average", G_TYPE_UINT64, &rtt_avg,
                                "r-squared", G_TYPE_DOUBLE, &r2, NULL))
        g_print ("годинник: RTT %.2f мс, r² = %.5f\n", rtt_avg / 1.0e6, r2);
      break;
    }
    default:
      break;
  }
  return TRUE;
}
