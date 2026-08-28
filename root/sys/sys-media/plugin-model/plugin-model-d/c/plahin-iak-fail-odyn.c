static gboolean
plugin_init (GstPlugin * plugin)
{
  return gst_element_register (plugin, "myfilter", GST_RANK_NONE,
      GST_TYPE_MY_FILTER);
}

GST_PLUGIN_DEFINE (GST_VERSION_MAJOR, GST_VERSION_MINOR,
    myfilter,                          /* коротке ім'я плагіна */
    "Приклад власного фільтра",
    plugin_init, "1.0", "LGPL", "myplugins", "https://example.org")
