/* Забрати все, що вже лежить на шині, і нічого не чекати.
   Потрібно після провалу: причина вже надіслана й лежить там. */
static void
drain_bus (Driver *d)
{
  GstMessage *msg;

  while ((msg = gst_bus_pop (d->bus)) != NULL) {
    handle_message (d, msg);
    gst_message_unref (msg);
  }
}

/* Дочекатися завершення попереднього наповнення, не гублячи решти повідомлень.
   TRUE — наповнення завершилося; FALSE — помилка, кінець потоку або таймаут. */
static gboolean
wait_for_async_done (Driver *d, GstClockTime limit)
{
  gint64 deadline = g_get_monotonic_time () + limit / GST_USECOND;

  for (;;) {
    gint64 left_us = deadline - g_get_monotonic_time ();
    GstMessage *msg;

    if (left_us <= 0) {
      g_printerr ("наповнення не завершилося за відведений час\n");
      return FALSE;
    }

    msg = gst_bus_timed_pop_filtered (d->bus, left_us * GST_USECOND, GST_MESSAGE_ANY);
    if (msg == NULL)
      continue;                    /* час вийшов — вирішить перевірка вгорі */

    if (GST_MESSAGE_TYPE (msg) == GST_MESSAGE_ASYNC_DONE &&
        GST_MESSAGE_SRC (msg) == GST_OBJECT (d->pipeline)) {
      gst_message_unref (msg);
      return TRUE;
    }

    handle_message (d, msg);
    gst_message_unref (msg);

    if (d->quit)                   /* ERROR або EOS прилетіли раніше за наповнення */
      return FALSE;
  }
}
