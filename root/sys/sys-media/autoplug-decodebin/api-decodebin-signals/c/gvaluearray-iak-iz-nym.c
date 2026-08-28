static GValueArray *
on_autoplug_sort (GstElement *bin, GstPad *pad, GstCaps *caps,
                  GValueArray *factories, gpointer user_data)
{
  GValueArray *result = g_value_array_new (factories->n_values);

  /* пропускаємо все, що зареєстроване як апаратне, а решту лишаємо як є */
  for (guint i = 0; i < factories->n_values; i++) {
    GValue *v = g_value_array_get_nth (factories, i);
    GstElementFactory *f = GST_ELEMENT_FACTORY (g_value_get_object (v));

    if (gst_element_factory_list_is_type (f,
            GST_ELEMENT_FACTORY_TYPE_HARDWARE))
      continue;

    g_value_array_append (result, v);
  }

  return result;               /* володіння переходить до decodebin */
}
