static gboolean
plugin_init (GstPlugin * plugin)
{
  GST_DEBUG_CATEGORY_INIT (myfilter_debug, "myfilter", 0,
      "інвертор яскравості GRAY8");

  return gst_element_register (plugin, "myfilter", GST_RANK_NONE,
      GST_TYPE_MY_FILTER);
}

#ifndef PACKAGE
#define PACKAGE "gst-myfilter"
#endif
#ifndef VERSION
#define VERSION "1.0"
#endif

GST_PLUGIN_DEFINE (GST_VERSION_MAJOR, GST_VERSION_MINOR,
    myfilter,                                     /* коротке ім'я плагіна */
    "Інвертор яскравості для перевірки моделі плагінів",
    plugin_init, VERSION, "LGPL", "myplugins", "https://example.org/")
