GstEvent * gst_event_new_flush_start  (void);
GstEvent * gst_event_new_flush_stop   (gboolean reset_time);
void       gst_event_parse_flush_stop (GstEvent *event, gboolean *reset_time);

GstEvent * gst_event_new_segment      (const GstSegment *segment);
void       gst_event_parse_segment    (GstEvent *event, const GstSegment **segment);
void       gst_event_copy_segment     (GstEvent *event, GstSegment *segment);

GstEvent * gst_event_new_segment_done   (GstFormat format, gint64 position);
void       gst_event_parse_segment_done (GstEvent *event, GstFormat *format,
                                         gint64 *position);

GstEvent * gst_event_new_instant_rate_change   (gdouble rate_multiplier,
                                                GstSegmentFlags new_flags);
void       gst_event_parse_instant_rate_change (GstEvent *event,
                                                gdouble *rate_multiplier,
                                                GstSegmentFlags *new_flags);
GstEvent * gst_event_new_instant_rate_sync_time (gdouble rate_multiplier,
                                                 GstClockTime running_time,
                                                 GstClockTime upstream_running_time);

GstEvent * gst_event_new_step (GstFormat format, guint64 amount, gdouble rate,
                               gboolean flush, gboolean intermediate);
