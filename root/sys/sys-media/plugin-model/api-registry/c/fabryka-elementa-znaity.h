/* transfer full, nullable — фабрика за іменем */
GstElementFactory *gst_element_factory_find   (const gchar *name);

/* transfer floating, nullable — знайти фабрику й одразу створити елемент;
   name=NULL → ім'я породжується само й буде неповторним у процесі */
GstElement *gst_element_factory_make          (const gchar *factoryname,
                                               const gchar *name);

/* те саме плюс властивості одразу, перелік завершує NULL (з 1.20) */
GstElement *gst_element_factory_make_full     (const gchar *factoryname,
                                               const gchar *first, ...);

/* те саме масивами, зручно з мов-обгорток (з 1.20) */
GstElement *gst_element_factory_make_with_properties
                                              (const gchar *factoryname,
                                               guint n,
                                               const gchar **names,
                                               const GValue *values);

/* створити з уже знайденої фабрики */
GstElement *gst_element_factory_create        (GstElementFactory *factory,
                                               const gchar *name);
GstElement *gst_element_factory_create_with_properties
                                              (GstElementFactory *factory,
                                               guint n,
                                               const gchar **names,
                                               const GValue *values);

/* 0, поки плагін не завантажено */
GType        gst_element_factory_get_element_type (GstElementFactory *factory);

/* transfer none — метадані з реєстру, файл не відкривається */
const gchar *gst_element_factory_get_metadata (GstElementFactory *factory,
                                               const gchar *key);
gchar **     gst_element_factory_get_metadata_keys (GstElementFactory *factory);

/* transfer none — шаблони падів разом із їхніми caps */
const GList *gst_element_factory_get_static_pad_templates (GstElementFactory *factory);
guint        gst_element_factory_get_num_pad_templates    (GstElementFactory *factory);

/* швидка перевірка сумісності за шаблонами, без створення елемента */
gboolean gst_element_factory_can_sink_all_caps (GstElementFactory *f, const GstCaps *caps);
gboolean gst_element_factory_can_sink_any_caps (GstElementFactory *f, const GstCaps *caps);
gboolean gst_element_factory_can_src_all_caps  (GstElementFactory *f, const GstCaps *caps);
gboolean gst_element_factory_can_src_any_caps  (GstElementFactory *f, const GstCaps *caps);

/* URI-схеми й інтерфейси, оголошені фабрикою */
GstURIType            gst_element_factory_get_uri_type      (GstElementFactory *factory);
const gchar * const * gst_element_factory_get_uri_protocols (GstElementFactory *factory);
gboolean              gst_element_factory_has_interface     (GstElementFactory *factory,
                                                             const gchar *interfacename);
