gboolean gst_plugin_register_static (gint major_version, gint minor_version,
                                     const gchar *name,
                                     const gchar *description,
                                     GstPluginInitFunc init_func,
                                     const gchar *version,
                                     const gchar *license,
                                     const gchar *source,
                                     const gchar *package,
                                     const gchar *origin);

/* те саме, але init_func отримує ще й user_data */
gboolean gst_plugin_register_static_full (…, gpointer user_data);
