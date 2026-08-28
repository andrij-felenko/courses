GstQuery * gst_query_new_position   (GstFormat format);
void       gst_query_set_position   (GstQuery *q, GstFormat format, gint64 cur);
void       gst_query_parse_position (GstQuery *q, GstFormat *format, gint64 *cur);

GstQuery * gst_query_new_duration   (GstFormat format);
void       gst_query_set_duration   (GstQuery *q, GstFormat format, gint64 duration);
void       gst_query_parse_duration (GstQuery *q, GstFormat *format, gint64 *duration);

GstQuery * gst_query_new_latency    (void);
void       gst_query_set_latency    (GstQuery *q, gboolean live,
                                     GstClockTime min_latency, GstClockTime max_latency);
void       gst_query_parse_latency  (GstQuery *q, gboolean *live,
                                     GstClockTime *min_latency, GstClockTime *max_latency);

GstQuery * gst_query_new_seeking    (GstFormat format);
void       gst_query_set_seeking    (GstQuery *q, GstFormat format, gboolean seekable,
                                     gint64 segment_start, gint64 segment_end);
void       gst_query_parse_seeking  (GstQuery *q, GstFormat *format, gboolean *seekable,
                                     gint64 *segment_start, gint64 *segment_end);

GstQuery * gst_query_new_convert    (GstFormat src_format, gint64 value,
                                     GstFormat dest_format);
void       gst_query_set_convert    (GstQuery *q, GstFormat src_format, gint64 src_value,
                                     GstFormat dest_format, gint64 dest_value);

GstQuery * gst_query_new_segment    (GstFormat format);
void       gst_query_set_segment    (GstQuery *q, gdouble rate, GstFormat format,
                                     gint64 start_value, gint64 stop_value);

GstQuery * gst_query_new_formats    (void);
void       gst_query_set_formatsv   (GstQuery *q, gint n_formats, const GstFormat *formats);

GstQuery * gst_query_new_uri        (void);
void       gst_query_set_uri        (GstQuery *q, const gchar *uri);
void       gst_query_parse_uri      (GstQuery *q, gchar **uri);   /* g_free */
