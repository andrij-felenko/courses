static void
on_deep_element_added (GstBin *pipeline, GstBin *sub_bin,
                       GstElement *element, gpointer user_data)
{
  GstElementFactory *f = gst_element_get_factory (element);   /* transfer none */
  if (f == NULL)
    return;

  const gchar *name = gst_plugin_feature_get_name (GST_PLUGIN_FEATURE (f));

  if (g_str_has_prefix (name, "avdec_"))
    g_object_set (element, "max-threads", 4, "output-corrupt", FALSE, NULL);
}
