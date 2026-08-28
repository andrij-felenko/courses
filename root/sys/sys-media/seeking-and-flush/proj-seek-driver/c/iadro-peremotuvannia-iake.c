typedef enum {
  SEEK_OK,        /* конвеєр наповнився на новій позиції */
  SEEK_REFUSED,   /* ніхто в ланцюгу не взявся виконувати */
  SEEK_PAST_END,  /* влучили за кінець матеріалу: прийшов EOS */
  SEEK_ERROR,     /* конвеєр зламався на новому місці */
  SEEK_TIMEOUT    /* мовчить: десь стоїть */
} SeekResult;

static const char *
seek_result_name (SeekResult r)
{
  static const char *n[] = { "готово", "відмовлено", "за кінцем",
                             "помилка", "таймаут" };
  return n[r];
}

/* Викинути з шини те, що накопичилося ДО нашого перемотування. Найтиповіше —
   ASYNC_DONE від наповнення на пуску: він лежить у черзі непрочитаний, бо
   gst_element_get_state() чекає на стан, а повідомлення з шини не забирає.
   ERROR навмисно не чіпаємо: його ми хочемо побачити. */
static void
drain_stale (Player *p)
{
  GstMessage *msg;

  while ((msg = gst_bus_pop_filtered (p->bus,
                  GST_MESSAGE_ASYNC_DONE | GST_MESSAGE_EOS)) != NULL)
    gst_message_unref (msg);
}

/* Перемотати з очищенням і дочекатися, доки конвеєр СПРАВДІ буде на новій
   позиції. У *spent_us — скільки це тривало, у мікросекундах. */
static SeekResult
seek_and_wait (Player *p, gint64 pos, GstSeekFlags flags, gint64 *spent_us)
{
  SeekResult res = SEEK_TIMEOUT;
  gint64 t0;

  /* Чекати на ASYNC_DONE має сенс ЛИШЕ з флашем: безфлашеве перемотування
     не робить конвеєр асинхронним, тож ASYNC_DONE не буде взагалі. */
  g_return_val_if_fail (flags & GST_SEEK_FLAG_FLUSH, SEEK_REFUSED);

  drain_stale (p);
  t0 = g_get_monotonic_time ();

  /* stop задаємо явним SET, а не GST_SEEK_TYPE_NONE: NONE лишив би чинним
     кінець від попереднього сегментного перемотування, і відтворення
     несподівано зупинилося б на межі старої петлі. */
  if (!gst_element_seek (p->pipeline, 1.0, GST_FORMAT_TIME, flags,
                         GST_SEEK_TYPE_SET, pos,
                         GST_SEEK_TYPE_SET, GST_CLOCK_TIME_NONE)) {
    *spent_us = g_get_monotonic_time () - t0;
    return SEEK_REFUSED;
  }

  for (;;) {
    gint64 spent = g_get_monotonic_time () - t0;
    GstMessage *msg;
    GstClockTime left;

    if ((GstClockTime) (spent * GST_USECOND) >= SEEK_TIMEOUT)
      break;
    /* чекаємо ЗАЛИШОК, а не повний таймаут: інакше кожне чуже повідомлення
       подовжує граничне чекання ще на десять секунд */
    left = SEEK_TIMEOUT - (GstClockTime) (spent * GST_USECOND);

    msg = gst_bus_timed_pop_filtered (p->bus, left,
              GST_MESSAGE_ASYNC_DONE | GST_MESSAGE_ERROR | GST_MESSAGE_EOS);
    if (!msg)
      break;                                  /* нічого не дочекалися */

    if (GST_MESSAGE_TYPE (msg) == GST_MESSAGE_ERROR) {
      GError *err = NULL;
      gchar  *dbg = NULL;

      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("  помилка від «%s»: %s\n",
                  GST_MESSAGE_SRC_NAME (msg), err->message);
      g_clear_error (&err);
      g_free (dbg);
      res = SEEK_ERROR;
    } else if (GST_MESSAGE_TYPE (msg) == GST_MESSAGE_EOS) {
      res = SEEK_PAST_END;
    } else if (GST_MESSAGE_SRC (msg) == GST_OBJECT (p->pipeline)) {
      /* ASYNC_DONE постить КОЖЕН приймач окремо, а конвеєр надсилає свій
         лише тоді, коли зібрав звіти всіх дітей. Потрібен саме конвеєрний. */
      res = SEEK_OK;
    } else {
      gst_message_unref (msg);
      continue;                               /* звіт однієї гілки — чекаємо решти */
    }

    gst_message_unref (msg);
    break;
  }

  *spent_us = g_get_monotonic_time () - t0;
  return res;
}

static gint64
position_now (Player *p)
{
  gint64 pos = GST_CLOCK_TIME_NONE;

  gst_element_query_position (p->pipeline, GST_FORMAT_TIME, &pos);
  return pos;
}
