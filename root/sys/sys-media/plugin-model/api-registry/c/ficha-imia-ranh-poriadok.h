/* насправді макрос: gst_plugin_feature_get_name(f) → GST_OBJECT_NAME(f) */
const gchar *gst_plugin_feature_get_name        (GstPluginFeature *feature);

guint        gst_plugin_feature_get_rank        (GstPluginFeature *feature);
void         gst_plugin_feature_set_rank        (GstPluginFeature *feature,
                                                 guint rank);

/* transfer full, nullable — плагін, який дав цю фічу */
GstPlugin *  gst_plugin_feature_get_plugin      (GstPluginFeature *feature);
/* transfer none, nullable — лише коротке ім'я плагіна (з 1.2) */
const gchar *gst_plugin_feature_get_plugin_name (GstPluginFeature *feature);

/* transfer full — завантажити плагін і повернути «повноцінну» фічу */
GstPluginFeature *gst_plugin_feature_load       (GstPluginFeature *feature);

gboolean gst_plugin_feature_check_version (GstPluginFeature *feature,
                                           guint min_major, guint min_minor,
                                           guint min_micro);

/* GCompareFunc для g_list_sort */
gint  gst_plugin_feature_rank_compare_func (gconstpointer p1, gconstpointer p2);

void   gst_plugin_feature_list_free  (GList *list);
GList *gst_plugin_feature_list_copy  (GList *list);
void   gst_plugin_feature_list_debug (GList *list);
