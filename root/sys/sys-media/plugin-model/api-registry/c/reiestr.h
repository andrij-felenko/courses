/* transfer none — сталий об'єкт процесу, unref не потрібен */
GstRegistry *      gst_registry_get                     (void);

/* transfer full, nullable — фіча заданого виду за іменем */
GstPluginFeature * gst_registry_find_feature            (GstRegistry *registry,
                                                         const gchar *name,
                                                         GType type);

/* transfer full, nullable — фіча за іменем, вид байдужий */
GstPluginFeature * gst_registry_lookup_feature          (GstRegistry *registry,
                                                         const char *name);

/* transfer full — усі фічі заданого виду */
GList *            gst_registry_get_feature_list        (GstRegistry *registry,
                                                         GType type);

/* transfer full — усі фічі, які дав один плагін */
GList *            gst_registry_get_feature_list_by_plugin
                                                        (GstRegistry *registry,
                                                         const gchar *name);

/* transfer full — усі відомі плагіни */
GList *            gst_registry_get_plugin_list         (GstRegistry *registry);

/* transfer full, nullable — плагін за коротким іменем */
GstPlugin *        gst_registry_find_plugin             (GstRegistry *registry,
                                                         const gchar *name);

/* transfer full — власний відбір: filter кличуть на кожну фічу;
   first=TRUE зупиняє пошук на першій, що підійшла */
GList *            gst_registry_feature_filter          (GstRegistry *registry,
                                                         GstPluginFeatureFilter filter,
                                                         gboolean first,
                                                         gpointer user_data);

/* чи є така фіча й чи не старіша вона за задану версію */
gboolean           gst_registry_check_feature_version   (GstRegistry *registry,
                                                         const gchar *feature_name,
                                                         guint min_major,
                                                         guint min_minor,
                                                         guint min_micro);

/* лічильник змін переліку фіч */
guint32            gst_registry_get_feature_list_cookie (GstRegistry *registry);

/* просканувати теку негайно; TRUE, якщо реєстр змінився */
gboolean           gst_registry_scan_path               (GstRegistry *registry,
                                                         const gchar *path);
