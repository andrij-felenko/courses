#include <gst/gst.h>

int
main (int argc, char *argv[])
{
  gst_init (&argc, &argv);

  if (argc < 2) {
    g_printerr ("вжиток: %s <ім'я-елемента>\n", argv[0]);
    return 2;
  }

  GstRegistry *registry = gst_registry_get ();          /* transfer none */
  GstPluginFeature *feature =
      gst_registry_find_feature (registry, argv[1], GST_TYPE_ELEMENT_FACTORY);

  if (feature == NULL) {
    g_print ("%s: у реєстрі немає такої фабрики\n", argv[1]);
    return 1;
  }

  GstElementFactory *factory = GST_ELEMENT_FACTORY (feature);

  g_print ("фабрика   %s\n", gst_plugin_feature_get_name (feature));
  g_print ("ранг      %u\n", gst_plugin_feature_get_rank (feature));
  g_print ("klass     %s\n",
      gst_element_factory_get_metadata (factory, GST_ELEMENT_METADATA_KLASS));
  g_print ("назва     %s\n",
      gst_element_factory_get_metadata (factory, GST_ELEMENT_METADATA_LONGNAME));

  GstPlugin *plugin = gst_plugin_feature_get_plugin (feature);   /* transfer full */
  if (plugin != NULL) {
    g_print ("плагін    %s (набір %s, ліцензія %s)\n",
        gst_plugin_get_name (plugin), gst_plugin_get_source (plugin),
        gst_plugin_get_license (plugin));
    g_print ("файл      %s\n", gst_plugin_get_filename (plugin));
    g_print ("файл відкрито: %s\n",
        gst_plugin_is_loaded (plugin) ? "так" : "ні");
    gst_object_unref (plugin);
  }

  /* аж ось тут plugin_init нарешті виконають */
  GstElement *element = gst_element_factory_create (factory, NULL);
  g_print ("створено  %s\n", GST_OBJECT_NAME (element));
  gst_object_unref (element);

  gst_object_unref (feature);
  return 0;
}
