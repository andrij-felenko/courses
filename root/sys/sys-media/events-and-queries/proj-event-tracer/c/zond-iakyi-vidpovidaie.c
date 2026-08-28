/* Зонд, що ВІДПОВІДАЄ замість елемента: перехоплює запит про тривалість,
   вписує в нього десять секунд і закриває питання. */
static GstPadProbeReturn
answer_duration (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  GstQuery *query = GST_PAD_PROBE_INFO_QUERY (info);
  GstFormat format;

  if (GST_PAD_PROBE_INFO_TYPE (info) & GST_PAD_PROBE_TYPE_PULL)
    return GST_PAD_PROBE_OK;                  /* це вже дорога назад */
  if (GST_QUERY_TYPE (query) != GST_QUERY_DURATION)
    return GST_PAD_PROBE_OK;

  gst_query_parse_duration (query, &format, NULL);
  if (format != GST_FORMAT_TIME)
    return GST_PAD_PROBE_OK;                  /* у байтах не відповідаємо */

  gst_query_set_duration (query, GST_FORMAT_TIME, 10 * GST_SECOND);
  /* НЕ звільняємо: об'єкт запиту належить тому, хто питав. */
  return GST_PAD_PROBE_HANDLED;
}

static void
ask_duration (GstPad *pad)
{
  GstQuery *query = gst_query_new_duration (GST_FORMAT_TIME);
  gint64 dur;

  if (gst_pad_query (pad, query)) {            /* синхронно, у нашій нитці */
    gst_query_parse_duration (query, NULL, &dur);
    g_print ("тривалість: %" GST_TIME_FORMAT "\n", GST_TIME_ARGS (dur));
  } else {
    g_print ("тривалість: ніхто не відповів\n");
  }
  gst_query_unref (query);                     /* створили ми — нам і звільняти */
}

static gboolean
duration_demo (gpointer data)
{
  GstPad *qsrc = data;
  gulong id;

  g_print ("\n--- питаємо тривалість у живого конвеєра ---\n");
  ask_duration (qsrc);

  id = gst_pad_add_probe (qsrc, GST_PAD_PROBE_TYPE_QUERY_UPSTREAM,
                          answer_duration, NULL, NULL);
  g_print ("--- те саме питання із зондом-відповідачем ---\n");
  ask_duration (qsrc);
  gst_pad_remove_probe (qsrc, id);

  return G_SOURCE_REMOVE;
}
