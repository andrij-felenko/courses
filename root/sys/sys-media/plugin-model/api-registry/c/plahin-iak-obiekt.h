/* transfer full — завантажити файл у процес; повертає ту саму або нову
   «завантажену» обгортку, стару після цього не вживають */
GstPlugin *gst_plugin_load         (GstPlugin *plugin);
GstPlugin *gst_plugin_load_by_name (const gchar *name);
GstPlugin *gst_plugin_load_file    (const gchar *filename, GError **error);

/* усе нижче — transfer none, беруть із дескриптора */
const gchar *gst_plugin_get_name                 (GstPlugin *plugin);
const gchar *gst_plugin_get_description          (GstPlugin *plugin);
const gchar *gst_plugin_get_filename             (GstPlugin *plugin);
const gchar *gst_plugin_get_license              (GstPlugin *plugin);
const gchar *gst_plugin_get_source               (GstPlugin *plugin);
const gchar *gst_plugin_get_package              (GstPlugin *plugin);
const gchar *gst_plugin_get_origin               (GstPlugin *plugin);
const gchar *gst_plugin_get_version              (GstPlugin *plugin);
const gchar *gst_plugin_get_release_date_string  (GstPlugin *plugin);

gboolean     gst_plugin_is_loaded                (GstPlugin *plugin);

const GstStructure *gst_plugin_get_cache_data (GstPlugin *plugin);
void                gst_plugin_set_cache_data (GstPlugin *plugin,
                                               GstStructure *cache_data);
