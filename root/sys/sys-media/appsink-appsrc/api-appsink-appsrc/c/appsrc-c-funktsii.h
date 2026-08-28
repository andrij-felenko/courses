/* формат і опис потоку */
void             gst_app_src_set_caps        (GstAppSrc *appsrc, const GstCaps *caps);
GstCaps *        gst_app_src_get_caps        (GstAppSrc *appsrc);
void             gst_app_src_set_size        (GstAppSrc *appsrc, gint64 size);
gint64           gst_app_src_get_size        (GstAppSrc *appsrc);
void             gst_app_src_set_duration    (GstAppSrc *appsrc, GstClockTime duration); /* 1.10 */
GstClockTime     gst_app_src_get_duration    (GstAppSrc *appsrc);
void             gst_app_src_set_stream_type (GstAppSrc *appsrc, GstAppStreamType type);
GstAppStreamType gst_app_src_get_stream_type (GstAppSrc *appsrc);

/* межі черги й поточне заповнення */
void         gst_app_src_set_max_bytes   (GstAppSrc *appsrc, guint64 max);
guint64      gst_app_src_get_max_bytes   (GstAppSrc *appsrc);
void         gst_app_src_set_max_buffers (GstAppSrc *appsrc, guint64 max);      /* 1.20 */
guint64      gst_app_src_get_max_buffers (GstAppSrc *appsrc);
void         gst_app_src_set_max_time    (GstAppSrc *appsrc, GstClockTime max); /* 1.20 */
GstClockTime gst_app_src_get_max_time    (GstAppSrc *appsrc);
guint64      gst_app_src_get_current_level_bytes   (GstAppSrc *appsrc);
guint64      gst_app_src_get_current_level_buffers (GstAppSrc *appsrc);
GstClockTime gst_app_src_get_current_level_time    (GstAppSrc *appsrc);
void            gst_app_src_set_leaky_type (GstAppSrc *appsrc, GstAppLeakyType leaky); /* 1.20 */
GstAppLeakyType gst_app_src_get_leaky_type (GstAppSrc *appsrc);

/* затримка */
void gst_app_src_set_latency (GstAppSrc *appsrc, guint64 min, guint64 max);
void gst_app_src_get_latency (GstAppSrc *appsrc, guint64 *min, guint64 *max);

/* штовхання даних */
GstFlowReturn gst_app_src_push_buffer      (GstAppSrc *appsrc, GstBuffer *buffer);
GstFlowReturn gst_app_src_push_buffer_list (GstAppSrc *appsrc, GstBufferList *buffer_list); /* 1.14 */
GstFlowReturn gst_app_src_push_sample      (GstAppSrc *appsrc, GstSample *sample);          /* 1.6 */
GstFlowReturn gst_app_src_end_of_stream    (GstAppSrc *appsrc);

/* зворотні виклики */
void gst_app_src_set_callbacks (GstAppSrc *appsrc, GstAppSrcCallbacks *callbacks,
                                gpointer user_data, GDestroyNotify notify);
void gst_app_src_set_simple_callbacks (GstAppSrc *appsrc, GstAppSrcSimpleCallbacks *cb); /* 1.28 */
