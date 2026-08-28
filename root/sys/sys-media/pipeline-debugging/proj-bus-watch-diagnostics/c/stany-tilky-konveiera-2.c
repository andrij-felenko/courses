static gboolean diag_bus (GstBus *bus, GstMessage *msg, gpointer data)
{
  Diag *d = data;
  (void) bus;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ERROR:
      diag_report (d, msg, "ПОМИЛКА");
      diag_dump (d, "error");        /* докази — у мілісекунду аварії */
      break;
    case GST_MESSAGE_WARNING:
      diag_report (d, msg, "ПОПЕРЕДЖЕННЯ");
      break;
    case GST_MESSAGE_INFO:
      diag_report (d, msg, "ВІДОМІСТЬ");
      break;

    /* … гілки ELEMENT, QOS і STATE_CHANGED з блоків вище … */

    default:
      break;
  }
  return TRUE;    /* лишаємось підключеними; msg НЕ звільняємо — він позичений */
}
