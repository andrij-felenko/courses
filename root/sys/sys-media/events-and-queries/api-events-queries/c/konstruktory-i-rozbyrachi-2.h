GstEvent * gst_event_new_qos   (GstQOSType type, gdouble proportion,
                                GstClockTimeDiff diff, GstClockTime timestamp);
void       gst_event_parse_qos (GstEvent *event, GstQOSType *type, gdouble *proportion,
                                GstClockTimeDiff *diff, GstClockTime *timestamp);

typedef enum {
  GST_QOS_TYPE_OVERFLOW  = 0,   /* не встигаємо: даних більше, ніж обробляється */
  GST_QOS_TYPE_UNDERFLOW = 1,   /* даних бракує */
  GST_QOS_TYPE_THROTTLE  = 2    /* навмисне сповільнення на вимогу */
} GstQOSType;

GstEvent * gst_event_new_seek   (gdouble rate, GstFormat format, GstSeekFlags flags,
                                 GstSeekType start_type, gint64 start,
                                 GstSeekType stop_type, gint64 stop);
void       gst_event_parse_seek (GstEvent *event, gdouble *rate, GstFormat *format,
                                 GstSeekFlags *flags,
                                 GstSeekType *start_type, gint64 *start,
                                 GstSeekType *stop_type, gint64 *stop);

GstEvent * gst_event_new_step   (GstFormat format, guint64 amount, gdouble rate,
                                 gboolean flush, gboolean intermediate);
GstEvent * gst_event_new_select_streams (GList *streams);       /* transfer none */
GstEvent * gst_event_new_instant_rate_change (gdouble rate_multiplier,
                                              GstSegmentFlags new_flags);
