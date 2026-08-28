typedef struct {
  Player    *p;
  GMainLoop *loop;
  gboolean   busy;         /* перемотування в польоті */
  gboolean   pending;      /* поки летіло, повзунок поїхав далі */
  gint64     pending_pos;
  guint      moves_left;
} Scrubber;

/* Надіслати й НЕ чекати: чекання зробить обробник шини. */
static void
scrub_fire (Scrubber *s, gint64 pos)
{
  s->busy = gst_element_seek (s->p->pipeline, 1.0, GST_FORMAT_TIME,
                              GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_KEY_UNIT,
                              GST_SEEK_TYPE_SET, pos,
                              GST_SEEK_TYPE_SET, GST_CLOCK_TIME_NONE);
}

/* Повзунок поїхав. Якщо попереднє прохання ще в польоті, другого не шлемо —
   лише запам'ятовуємо останнє положення. */
static void
scrub_to (Scrubber *s, gint64 pos)
{
  if (s->busy) {
    s->pending = TRUE;
    s->pending_pos = pos;
  } else {
    scrub_fire (s, pos);
  }
}

static gboolean
scrub_bus (GstBus *bus, GstMessage *msg, gpointer data)
{
  Scrubber *s = data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ASYNC_DONE:
      if (GST_MESSAGE_SRC (msg) != GST_OBJECT (s->p->pipeline))
        break;                                /* звіт окремої гілки — не наш */
      s->busy = FALSE;
      g_print ("кадр на %" GST_TIME_FORMAT "\n",
               GST_TIME_ARGS (position_now (s->p)));
      if (s->pending) {
        s->pending = FALSE;
        scrub_fire (s, s->pending_pos);       /* ОСТАННЄ, а не наступне за чергою */
      }
      break;

    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar  *dbg = NULL;

      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("помилка від «%s»: %s\n",
                  GST_MESSAGE_SRC_NAME (msg), err->message);
      g_clear_error (&err);
      g_free (dbg);
      g_main_loop_quit (s->loop);
      break;
    }

    default:
      break;
  }
  return TRUE;                                /* спостерігач лишається на шині */
}

/* Імітація руки: сорок положень за дві секунди — швидше, ніж конвеєр устигає. */
static gboolean
scrub_tick (gpointer data)
{
  Scrubber *s = data;
  gint64 span;

  if (s->moves_left == 0) {
    g_main_loop_quit (s->loop);
    return G_SOURCE_REMOVE;
  }
  /* ведемо повзунок у ДОЗВОЛЕНИХ межах, а не від нуля до тривалості:
     у кільцевому буфері мережевого джерела лівий край повзе вперед */
  span = s->p->hi - s->p->lo;
  scrub_to (s, s->p->lo + span / 40 * (40 - s->moves_left));
  s->moves_left--;
  return G_SOURCE_CONTINUE;
}
