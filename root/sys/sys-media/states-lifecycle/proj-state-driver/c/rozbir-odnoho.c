/* Розібрати одне повідомлення. Викликається ЛИШЕ з головного потоку —
   тому тут вільно чіпати стан конвеєра. */
static void
handle_message (Driver *d, GstMessage *msg)
{
  switch (GST_MESSAGE_TYPE (msg)) {

    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar  *dbg = NULL;

      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("ПОМИЛКА від «%s»: %s\n", GST_MESSAGE_SRC_NAME (msg), err->message);
      if (dbg)
        g_printerr ("  подробиці: %s\n", dbg);
      g_clear_error (&err);
      g_free (dbg);

      d->failed = TRUE;
      d->quit = TRUE;
      break;
    }

    case GST_MESSAGE_WARNING: {
      GError *err = NULL;
      gchar  *dbg = NULL;

      gst_message_parse_warning (msg, &err, &dbg);
      g_printerr ("попередження від «%s»: %s\n", GST_MESSAGE_SRC_NAME (msg), err->message);
      g_clear_error (&err);
      g_free (dbg);
      break;                       /* конвеєр живий — не виходимо */
    }

    case GST_MESSAGE_EOS:
      g_print ("потік дійшов кінця\n");
      d->quit = TRUE;
      break;

    case GST_MESSAGE_STATE_CHANGED:
      /* діти звітують сюди теж; нас цікавить лише сам конвеєр */
      if (GST_MESSAGE_SRC (msg) == GST_OBJECT (d->pipeline)) {
        GstState old_state, new_state, pending;

        gst_message_parse_state_changed (msg, &old_state, &new_state, &pending);
        g_print ("конвеєр: %s → %s%s\n",
                 gst_element_state_get_name (old_state),
                 gst_element_state_get_name (new_state),
                 pending == GST_STATE_VOID_PENDING ? "" : " (є ще незавершене)");
      }
      break;

    case GST_MESSAGE_CLOCK_LOST:
      /* елемент, що давав годинник, зник; новий вибирається лише
         на переході в PLAYING — тож зробимо цей перехід примусово */
      g_print ("годинник утрачено — перевибираємо\n");
      gst_element_set_state (d->pipeline, GST_STATE_PAUSED);
      gst_element_set_state (d->pipeline, GST_STATE_PLAYING);
      break;

    case GST_MESSAGE_APPLICATION:
      /* записка від потоків конвеєра до нас — про це далі */
      if (gst_message_has_name (msg, "app-stop"))
        d->quit = TRUE;
      break;

    default:
      break;
  }
}
