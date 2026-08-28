GList *cands = gst_element_factory_list_get_elements (
    GST_ELEMENT_FACTORY_TYPE_DECODER | GST_ELEMENT_FACTORY_TYPE_MEDIA_VIDEO,
    GST_RANK_MARGINAL);

GstCaps *caps = gst_caps_from_string ("video/x-h264");
GList *fit = gst_element_factory_list_filter (cands, caps, GST_PAD_SINK, FALSE);
fit = g_list_sort (fit, gst_plugin_feature_rank_compare_func);

for (GList *l = fit; l != NULL; l = l->next) {
  GstPluginFeature *f = GST_PLUGIN_FEATURE (l->data);
  g_print ("%-18s rank %u\n", gst_plugin_feature_get_name (f),
      gst_plugin_feature_get_rank (f));
}

gst_plugin_feature_list_free (fit);
gst_plugin_feature_list_free (cands);
gst_caps_unref (caps);
