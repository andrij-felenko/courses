/* Спрацьовує один раз, якщо за guard_sec секунд PLAYING так і не настав. */
static gboolean diag_guard (gpointer data)
{
  Diag *d = data;
  GstState cur = GST_STATE_VOID_PENDING, pending = GST_STATE_VOID_PENDING;

  /* НУЛЬОВА витримка: питаємо, що є ЗАРАЗ, і не чекаємо ні миті.
     GST_CLOCK_TIME_NONE тут означало б «висни разом із конвеєром». */
  GstStateChangeReturn ret = gst_element_get_state (d->pipeline, &cur, &pending, 0);

  g_printerr ("СТОРОЖ: за %u с конвеєр не дійшов до PLAYING\n", d->guard_sec);
  g_printerr ("  зараз:   %s\n", gst_element_state_get_name (cur));
  g_printerr ("  у черзі: %s\n", gst_element_state_get_name (pending));
  g_printerr ("  перехід: %s\n", gst_element_state_change_return_get_name (ret));

  if (cur == GST_STATE_PAUSED && !d->is_live)
    g_printerr ("  → перший буфер не дійшов до стоку: розрив десь між ними\n");
  else if (cur == GST_STATE_PAUSED)
    g_printerr ("  → джерело живе, PAUSED тут не діагноз: дивись, чому нема PLAYING\n");
  else if (cur == GST_STATE_READY)
    g_printerr ("  → не вийшли з READY: джерело не відкрилося\n");
  else if (cur == GST_STATE_NULL)
    g_printerr ("  → конвеєр у NULL: set_state або не викликали, або він відкотився\n");

  diag_dump (d, "stuck");
  d->guard_id = 0;
  return G_SOURCE_REMOVE;      /* доповіли один раз — далі не набридаємо */
}
