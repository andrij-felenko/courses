/* Гілка — окремий бін з одним привидним sink-падом. Так її можна додати,
   синхронізувати, від'єднати й вилучити як одне ціле. */
static GstElement *
make_branch (const gchar *name, const gchar *const *factories, GstElement **tail)
{
  GstElement *bin = gst_bin_new (name);
  GstElement *first = NULL, *prev = NULL;

  for (int i = 0; factories[i] != NULL; i++) {
    GstElement *e = gst_element_factory_make (factories[i], NULL);
    if (e == NULL) {
      g_printerr ("немає елемента '%s' — бракує плагіна\n", factories[i]);
      gst_object_unref (bin);
      return NULL;
    }
    gst_bin_add (GST_BIN (bin), e);          /* бін забирає посилання на e */
    if (prev != NULL && !gst_element_link (prev, e)) {
      g_printerr ("не з'єдналися %s → %s\n", factories[i - 1], factories[i]);
      gst_object_unref (bin);
      return NULL;
    }
    if (first == NULL)
      first = e;
    prev = e;
  }

  /* Вхід біна: привид над sink-падом першого елемента. Бін щойно створений,
     тобто в стані NULL, — активувати пад окремо не треба, це зробить перехід
     стану. Пад, доданий до елемента, який ВЖЕ працює, довелося б активувати
     самому: gst_pad_set_active (ghost, TRUE). */
  GstPad *inner = gst_element_get_static_pad (first, "sink");
  GstPad *ghost = gst_ghost_pad_new ("sink", inner);
  gst_element_add_pad (bin, ghost);          /* бін забирає посилання на ghost */
  gst_object_unref (inner);

  if (tail != NULL)
    *tail = prev;              /* позичений покажчик: власник — бін */
  return bin;
}
