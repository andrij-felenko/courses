/* формат і режим роботи */
void          gst_app_sink_set_caps      (GstAppSink *appsink, const GstCaps *caps);
GstCaps *     gst_app_sink_get_caps      (GstAppSink *appsink);
gboolean      gst_app_sink_is_eos        (GstAppSink *appsink);
void          gst_app_sink_set_emit_signals (GstAppSink *appsink, gboolean emit);
gboolean      gst_app_sink_get_emit_signals (GstAppSink *appsink);

/* межі внутрішньої черги */
void          gst_app_sink_set_max_buffers (GstAppSink *appsink, guint max);
guint         gst_app_sink_get_max_buffers (GstAppSink *appsink);
void          gst_app_sink_set_max_bytes   (GstAppSink *appsink, guint64 max);       /* 1.24 */
guint64       gst_app_sink_get_max_bytes   (GstAppSink *appsink);
void          gst_app_sink_set_max_time    (GstAppSink *appsink, GstClockTime max);  /* 1.24 */
GstClockTime  gst_app_sink_get_max_time    (GstAppSink *appsink);

/* поточне заповнення — 1.28 */
guint64       gst_app_sink_get_current_level_buffers (GstAppSink *appsink);
guint64       gst_app_sink_get_current_level_bytes   (GstAppSink *appsink);
GstClockTime  gst_app_sink_get_current_level_time    (GstAppSink *appsink);

/* поведінка при переповненні й на кінці потоку */
void            gst_app_sink_set_drop       (GstAppSink *appsink, gboolean drop);      /* застаріле з 1.28 */
gboolean        gst_app_sink_get_drop       (GstAppSink *appsink);
void            gst_app_sink_set_leaky_type (GstAppSink *appsink, GstAppLeakyType leaky); /* 1.28 */
GstAppLeakyType gst_app_sink_get_leaky_type (GstAppSink *appsink);
void            gst_app_sink_set_wait_on_eos (GstAppSink *appsink, gboolean wait);      /* 1.8 */
gboolean        gst_app_sink_get_wait_on_eos (GstAppSink *appsink);
void            gst_app_sink_set_buffer_list_support (GstAppSink *appsink, gboolean enable_lists);
gboolean        gst_app_sink_get_buffer_list_support (GstAppSink *appsink);

/* забирання даних — усе повертає transfer full */
GstSample *     gst_app_sink_pull_preroll     (GstAppSink *appsink);
GstSample *     gst_app_sink_pull_sample      (GstAppSink *appsink);
GstMiniObject * gst_app_sink_pull_object      (GstAppSink *appsink);                  /* 1.20 */
GstSample *     gst_app_sink_try_pull_preroll (GstAppSink *appsink, GstClockTime timeout); /* 1.10 */
GstSample *     gst_app_sink_try_pull_sample  (GstAppSink *appsink, GstClockTime timeout); /* 1.10 */
GstMiniObject * gst_app_sink_try_pull_object  (GstAppSink *appsink, GstClockTime timeout); /* 1.20 */

/* зворотні виклики */
void gst_app_sink_set_callbacks (GstAppSink *appsink, GstAppSinkCallbacks *callbacks,
                                 gpointer user_data, GDestroyNotify notify);
void gst_app_sink_set_simple_callbacks (GstAppSink *appsink, GstAppSinkSimpleCallbacks *cb); /* 1.28 */
