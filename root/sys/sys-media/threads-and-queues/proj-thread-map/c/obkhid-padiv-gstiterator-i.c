/* Повісити пробу на кожен пад одного елемента. Самого BUFFER мало:
   елемент може штовхати списки буферів, і тоді проба на самі лише
   буфери просто мовчить. */
static void
probe_pads (GstElement *elem)
{
  GstIterator *it = gst_element_iterate_pads (elem);
  GValue item = G_VALUE_INIT;
  gboolean done = FALSE;

  while (!done) {
    switch (gst_iterator_next (it, &item)) {
      case GST_ITERATOR_OK:
        gst_pad_add_probe (GST_PAD (g_value_get_object (&item)),
                           GST_PAD_PROBE_TYPE_BUFFER |
                           GST_PAD_PROBE_TYPE_BUFFER_LIST,
                           first_buffer, NULL, NULL);
        g_value_reset (&item);      /* GValue тримав посилання — віддаємо */
        break;
      case GST_ITERATOR_RESYNC:     /* список падів змінився під нами */
        gst_iterator_resync (it);   /* обхід починається спочатку */
        break;
      default:                      /* DONE або ERROR */
        done = TRUE;
        break;
    }
  }
  g_value_unset (&item);
  gst_iterator_free (it);
}

/* Те саме по всіх елементах конвеєра, разом із тими, що лежать усередині
   вкладених бінів: autovideosink — саме такий бін. */
static void
for_each_element (GstElement *pipeline, void (*fn) (GstElement *))
{
  GstIterator *it = gst_bin_iterate_recurse (GST_BIN (pipeline));
  GValue item = G_VALUE_INIT;
  gboolean done = FALSE;

  while (!done) {
    switch (gst_iterator_next (it, &item)) {
      case GST_ITERATOR_OK:
        fn (GST_ELEMENT (g_value_get_object (&item)));
        g_value_reset (&item);
        break;
      case GST_ITERATOR_RESYNC:
        gst_iterator_resync (it);
        break;
      default:
        done = TRUE;
        break;
    }
  }
  g_value_unset (&item);
  gst_iterator_free (it);
}
