/* Розбір помилки. Повідомлення НЕ звільняє — власник у різних дорогах різний. */
static void report_error (GstMessage *msg)
{
  GError *err = NULL;
  gchar  *dbg = NULL;
  gst_message_parse_error (msg, &err, &dbg);

  g_printerr ("ПОМИЛКА від %s: %s\n", src_name (msg), err->message);
  g_printerr ("  домен %s, код %d\n", g_quark_to_string (err->domain), err->code);

  if (g_error_matches (err, GST_RESOURCE_ERROR, GST_RESOURCE_ERROR_NOT_FOUND))
    g_printerr ("  → за цією адресою джерела немає\n");
  else if (g_error_matches (err, GST_STREAM_ERROR, GST_STREAM_ERROR_CODEC_NOT_FOUND))
    g_printerr ("  → у системі немає плагіна-декодера для цього формату\n");

  g_printerr ("  зневадження: %s\n", dbg ? dbg : "(немає)");

  g_clear_error (&err);
  g_free (dbg);
}

static gboolean on_bus_message (GstBus *bus, GstMessage *msg, gpointer data)
{
  App *app = data;

  switch (GST_MESSAGE_TYPE (msg)) {

    case GST_MESSAGE_ERROR:
      report_error (msg);
      app->exit_code = 1;
      g_main_loop_quit (app->loop);       /* конвеєр сам не спиниться */
      break;

    case GST_MESSAGE_EOS:
      g_print ("кінець потоку\n");
      g_main_loop_quit (app->loop);
      break;

    case GST_MESSAGE_WARNING: {
      GError *err = NULL;
      gchar  *dbg = NULL;
      gst_message_parse_warning (msg, &err, &dbg);
      g_printerr ("попередження від %s: %s (%s)\n",
                  src_name (msg), err->message, dbg ? dbg : "—");
      g_clear_error (&err);
      g_free (dbg);
      break;                              /* робота триває — не зупиняємо */
    }

    case GST_MESSAGE_STATE_CHANGED: {
      if (GST_MESSAGE_SRC (msg) != GST_OBJECT (app->pipeline))
        break;                            /* стани окремих елементів нас не цікавлять */
      GstState from, to, pending;
      gst_message_parse_state_changed (msg, &from, &to, &pending);
      g_print ("конвеєр: %s → %s\n",
               gst_element_state_get_name (from), gst_element_state_get_name (to));
      break;
    }

    case GST_MESSAGE_BUFFERING: {
      if (app->is_live)
        break;                            /* живому джерелу пауза лише зашкодить */
      gint percent = 0;
      gst_message_parse_buffering (msg, &percent);
      g_print ("буферизація %3d%%\n", percent);

      if (percent < 100) {
        if (!app->buffering && app->target == GST_STATE_PLAYING)
          gst_element_set_state (app->pipeline, GST_STATE_PAUSED);
        app->buffering = TRUE;
      } else if (app->buffering) {
        app->buffering = FALSE;
        if (app->target == GST_STATE_PLAYING)
          gst_element_set_state (app->pipeline, GST_STATE_PLAYING);
      }
      break;
    }

    case GST_MESSAGE_LATENCY:
      g_print ("перерахунок затримки на прохання %s\n", src_name (msg));
      gst_bin_recalculate_latency (GST_BIN (app->pipeline));
      break;

    case GST_MESSAGE_CLOCK_LOST:
      /* годинник зник; новий вибереться на наступному вході в PLAYING */
      gst_element_set_state (app->pipeline, GST_STATE_PAUSED);
      gst_element_set_state (app->pipeline, GST_STATE_PLAYING);
      break;

    default:
      break;
  }

  return TRUE;      /* лишаємось підключеними; msg НЕ звільняємо — він позичений */
}
