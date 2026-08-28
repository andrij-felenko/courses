/* Розбір ERROR / WARNING / INFO. Повідомлення позичене — НЕ звільняємо. */
static void diag_report (Diag *d, GstMessage *msg, const gchar *kind)
{
  GError *err = NULL;
  gchar  *dbg = NULL;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ERROR:   gst_message_parse_error   (msg, &err, &dbg); break;
    case GST_MESSAGE_WARNING: gst_message_parse_warning (msg, &err, &dbg); break;
    default:                  gst_message_parse_info    (msg, &err, &dbg); break;
  }

  gchar *path = src_path (msg);
  g_printerr ("%s: %s\n", kind, err ? err->message : "(без тексту)");
  g_printerr ("  елемент: %s\n", path);
  if (err)
    g_printerr ("  домен:   %s, код %d\n", g_quark_to_string (err->domain), err->code);
  /* Ось заради чого все: файл, рядок, функція і шлях у графі. */
  g_printerr ("  місце:   %s\n", dbg ? dbg : "(бібліотека не дала подробиць)");

  g_free (path);
  g_clear_error (&err);   /* GError виділено ЗА НАС — власник ми */
  g_free (dbg);           /* рядок теж наш */
}
