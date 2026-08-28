static GstAutoplugSelectResult
on_autoplug_select (GstElement *bin, GstPad *pad, GstCaps *caps,
                    GstElementFactory *factory, gpointer user_data)
{
  const gchar *name = gst_plugin_feature_get_name (GST_PLUGIN_FEATURE (factory));

  /* відомо, що на цьому залізі 10-бітний профіль апаратно не йде */
  if (g_str_has_prefix (name, "va") && caps_are_10bit (caps))
    return GST_AUTOPLUG_SELECT_SKIP;

  return GST_AUTOPLUG_SELECT_TRY;
}
