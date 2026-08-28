typedef struct {
  Player    *p;
  GMainLoop *loop;
  gint64     from, to;
  guint      laps_left;
} Looper;

/* Перший стрибок у петлю — З флашем: конвеєр треба вичистити від того, що в
   ньому було. SEGMENT каже: дійшовши до `to`, не оголошуй кінець потоку,
   а поклади SEGMENT_DONE на шину. */
static gboolean
loop_start (Looper *l)
{
  return gst_element_seek (l->p->pipeline, 1.0, GST_FORMAT_TIME,
                           GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_SEGMENT
                             | GST_SEEK_FLAG_ACCURATE,
                           GST_SEEK_TYPE_SET, l->from,
                           GST_SEEK_TYPE_SET, l->to);
}

static gboolean
loop_bus (GstBus *bus, GstMessage *msg, gpointer data)
{
  Looper *l = data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_SEGMENT_DONE:
      if (l->laps_left == 0) {
        /* Петля сама не скінчиться: SEGMENT задавив кінець потоку, і конвеєр
           просто стоятиме мовчки. Оголошуємо кінець власноруч. */
        gst_element_send_event (l->p->pipeline, gst_event_new_eos ());
        break;
      }
      l->laps_left--;
      /* БЕЗ флаша — у цьому весь сенс: старе дограється, нове стане за ним
         у чергу, і між колами не буде ані паузи, ані клацу. */
      if (!gst_element_seek (l->p->pipeline, 1.0, GST_FORMAT_TIME,
                             GST_SEEK_FLAG_SEGMENT | GST_SEEK_FLAG_ACCURATE,
                             GST_SEEK_TYPE_SET, l->from,
                             GST_SEEK_TYPE_SET, l->to))
        g_main_loop_quit (l->loop);
      break;

    case GST_MESSAGE_EOS:
      g_main_loop_quit (l->loop);
      break;

    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar  *dbg = NULL;

      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("помилка від «%s»: %s\n",
                  GST_MESSAGE_SRC_NAME (msg), err->message);
      g_clear_error (&err);
      g_free (dbg);
      g_main_loop_quit (l->loop);
      break;
    }

    default:
      break;
  }
  return TRUE;
}
