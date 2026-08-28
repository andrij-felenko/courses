static gboolean
bus_cb (GstBus *bus, GstMessage *msg, gpointer user_data)
{
  GstElement *pipeline = user_data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar  *dbg = NULL;
      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("%s | %s:%d | %s | %s\n",
                  GST_OBJECT_NAME (GST_MESSAGE_SRC (msg)),
                  g_quark_to_string (err->domain), err->code,
                  err->message, dbg ? dbg : "(без подробиць)");
      g_clear_error (&err);            /* GError — наш */
      g_free (dbg);                    /* рядок — теж наш */
      break;
    }
    case GST_MESSAGE_BUFFERING: {
      gint percent = 0;
      GstBufferingMode mode;
      gst_message_parse_buffering (msg, &percent);
      gst_message_parse_buffering_stats (msg, &mode, NULL, NULL, NULL);
      if (mode != GST_BUFFERING_LIVE)  /* живий конвеєр на паузу не ставимо */
        gst_element_set_state (pipeline,
            percent < 100 ? GST_STATE_PAUSED : GST_STATE_PLAYING);
      break;
    }
    case GST_MESSAGE_DEVICE_ADDED:     /* розширений тип: тільки через ==, не маскою */
      break;
    default:
      break;
  }
  return TRUE;                         /* FALSE зняло б стеження назавжди */
}

/* ── підключення ─────────────────────────────────────────────────────── */
GstBus  *bus = gst_element_get_bus (pipeline);   /* нове посилання */
GSource *src = gst_bus_create_watch (bus);       /* нове джерело, ще без колбека */

g_source_set_callback (src, G_SOURCE_FUNC (bus_cb), pipeline, NULL);
g_source_attach (src, my_context);               /* саме той контекст, який крутимо ми */

/* ── прибирання ──────────────────────────────────────────────────────── */
g_source_destroy (src);
g_source_unref (src);
gst_object_unref (bus);
