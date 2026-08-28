GstQuery * gst_query_new_seeking   (GstFormat format);
void       gst_query_set_seeking   (GstQuery *query, GstFormat format,
                                    gboolean seekable,
                                    gint64 segment_start, gint64 segment_end);
void       gst_query_parse_seeking (GstQuery *query, GstFormat *format,
                                    gboolean *seekable,
                                    gint64 *segment_start, gint64 *segment_end);

GstQuery * gst_query_new_position  (GstFormat format);
void       gst_query_parse_position (GstQuery *query, GstFormat *format, gint64 *cur);

GstQuery * gst_query_new_duration  (GstFormat format);
void       gst_query_parse_duration (GstQuery *query, GstFormat *format, gint64 *duration);

GstQuery * gst_query_new_segment   (GstFormat format);
void       gst_query_parse_segment (GstQuery *query, gdouble *rate, GstFormat *format,
                                    gint64 *start_value, gint64 *stop_value);
