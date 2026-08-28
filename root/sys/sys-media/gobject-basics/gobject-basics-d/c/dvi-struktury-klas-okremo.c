static void
gst_my_filter_class_init (GstMyFilterClass * klass)
{
  GstElementClass *element_class = GST_ELEMENT_CLASS (klass);

  /* після копіювання тут лежить реалізація GstElement; замінюємо своєю */
  element_class->change_state = gst_my_filter_change_state;

  gst_element_class_set_static_metadata (element_class,
      "My filter", "Filter/Effect/Video", "Приклад", "Автор <a@example.org>");
}
