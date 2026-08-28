GType
gst_my_filter_get_type (void)
{
  static gsize type = 0;
  if (g_once_init_enter (&type)) {
    GType t = g_type_register_static_simple (GST_TYPE_ELEMENT,
        "GstMyFilter",
        sizeof (GstMyFilterClass), (GClassInitFunc) gst_my_filter_class_init,
        sizeof (GstMyFilter),      (GInstanceInitFunc) gst_my_filter_init, 0);
    g_once_init_leave (&type, t);
  }
  return type;
}
