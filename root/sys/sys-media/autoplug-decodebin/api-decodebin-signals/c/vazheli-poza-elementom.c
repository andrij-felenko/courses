static void
set_rank (const gchar *factory, GstRank rank)
{
  GstPluginFeature *f = gst_registry_find_feature (gst_registry_get (),
      factory, GST_TYPE_ELEMENT_FACTORY);
  if (f == NULL)
    return;                      /* такої фабрики в системі немає */
  gst_plugin_feature_set_rank (f, rank);
  gst_object_unref (f);
}

/* прибрати програмний декодер з-під ніг апаратного */
set_rank ("avdec_h264", GST_RANK_NONE);
