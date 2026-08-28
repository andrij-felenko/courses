/* Пуск із розбором відповіді. FALSE — конвеєр навіть не почав. */
static gboolean diag_start (Diag *d)
{
  GstStateChangeReturn ret = gst_element_set_state (d->pipeline, GST_STATE_PAUSED);

  if (ret == GST_STATE_CHANGE_NO_PREROLL) {
    d->is_live = TRUE;
    g_printerr ("джерело живе: прероллу не буде, ASYNC_DONE теж не прийде\n");
  }

  if (ret != GST_STATE_CHANGE_FAILURE)
    ret = gst_element_set_state (d->pipeline, GST_STATE_PLAYING);

  if (ret == GST_STATE_CHANGE_FAILURE) {
    /* Помилка вже на шині, але головний цикл ще не крутиться, і стеження,
       хоч і приєднане, не спрацює. Забираємо руками — тією ж функцією. */
    GstMessage *msg = gst_bus_timed_pop_filtered (d->bus, 0, GST_MESSAGE_ERROR);
    if (msg) {
      diag_report (d, msg, "ПОМИЛКА ПУСКУ");
      gst_message_unref (msg);      /* а ЦЕ повідомлення наше — звільняємо */
    } else {
      g_printerr ("пуск не вдався, а помилки на шині немає\n");
    }
    diag_dump (d, "start-failed");
    return FALSE;
  }
  return TRUE;
}
