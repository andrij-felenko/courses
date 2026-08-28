/* Ширини в printf рахують БАЙТИ, а не літери, тож «%-6s» на кирилиці не
   вирівнює нічого. Тому кириличні колонки подано вже однакової довжини,
   а ширину задано лише латинським. */
static void
line_out (const Point *p, const gchar *kind, const gchar *dir,
          const gchar *ser, const gchar *name, const gchar *extra)
{
  g_print ("%6" G_GINT64_FORMAT " мс | %-10s | %-3s | %s %s %s | %-22s | буфер #%-4"
           G_GUINT64_FORMAT "%s\n",
           ms_now (), p->tag, thread_tag (), kind, dir, ser, name, p->buffers, extra);
}

static GstPadProbeReturn
trace_cb (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  Point *p = user_data;
  GstPadProbeType t = GST_PAD_PROBE_INFO_TYPE (info);
  const gchar *dir;

  /* Буфери лише рахуємо: якби ми їх друкували, рядки із сигналами потонули б
     у тридцяти рядках на секунду, а ще зонд почав би сам гальмувати конвеєр. */
  if (t & (GST_PAD_PROBE_TYPE_BUFFER | GST_PAD_PROBE_TYPE_BUFFER_LIST)) {
    p->buffers++;
    return GST_PAD_PROBE_OK;
  }

  /* Напрям — із типу зонда, а не з прапорців сигналу: у скидання
     й у всіх типів CUSTOM_BOTH увімкнено обидва біти напрямку. */
  dir = (t & (GST_PAD_PROBE_TYPE_EVENT_UPSTREAM |
              GST_PAD_PROBE_TYPE_QUERY_UPSTREAM)) ? "вгору" : "вниз ";

  if (t & (GST_PAD_PROBE_TYPE_EVENT_DOWNSTREAM |
           GST_PAD_PROBE_TYPE_EVENT_UPSTREAM |
           GST_PAD_PROBE_TYPE_EVENT_FLUSH)) {
    GstEvent *ev = GST_PAD_PROBE_INFO_EVENT (info);      /* позичений, не наш */
    const GstStructure *s = gst_event_get_structure (ev);
    gchar extra[64] = "";
    gint64 sent;

    /* Наші власні мітки несуть у собі мить надсилання — звідси й вимір. */
    if (s != NULL && gst_structure_has_name (s, "tracer-mark") &&
        gst_structure_get_int64 (s, "sent-ms", &sent))
      g_snprintf (extra, sizeof extra, "   ← у дорозі %" G_GINT64_FORMAT " мс",
                  ms_now () - sent);

    line_out (p, "подія ", dir,
              GST_EVENT_IS_SERIALIZED (ev) ? "сер." : "поз.",
              GST_EVENT_TYPE_NAME (ev), extra);
    return GST_PAD_PROBE_OK;
  }

  if (t & (GST_PAD_PROBE_TYPE_QUERY_DOWNSTREAM |
           GST_PAD_PROBE_TYPE_QUERY_UPSTREAM)) {
    GstQuery *q = GST_PAD_PROBE_INFO_QUERY (info);

    /* Запит проходить зонд ДВІЧІ: з бітом PUSH — дорогою по відповідь,
       з бітом PULL — назад, уже із заповненими полями. */
    line_out (p, (t & GST_PAD_PROBE_TYPE_PULL) ? "запит←" : "запит→", dir,
              GST_QUERY_IS_SERIALIZED (q) ? "сер." : "поз.",
              GST_QUERY_TYPE_NAME (q), "");
    return GST_PAD_PROBE_OK;
  }
  return GST_PAD_PROBE_OK;
}
