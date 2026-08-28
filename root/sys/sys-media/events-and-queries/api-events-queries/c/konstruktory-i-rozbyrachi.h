GstEvent * gst_event_new_flush_start   (void);
GstEvent * gst_event_new_flush_stop    (gboolean reset_time);
void       gst_event_parse_flush_stop  (GstEvent *event, gboolean *reset_time);

GstEvent * gst_event_new_stream_start  (const gchar *stream_id);
void       gst_event_parse_stream_start(GstEvent *event, const gchar **stream_id);
void       gst_event_set_group_id      (GstEvent *event, guint group_id);
gboolean   gst_event_parse_group_id    (GstEvent *event, guint *group_id);

GstEvent * gst_event_new_caps          (GstCaps *caps);          /* caps: transfer none */
void       gst_event_parse_caps        (GstEvent *event, GstCaps **caps);

GstEvent * gst_event_new_segment       (const GstSegment *segment);   /* копіює */
void       gst_event_parse_segment     (GstEvent *event, const GstSegment **segment);
void       gst_event_copy_segment      (GstEvent *event, GstSegment *segment);

GstEvent * gst_event_new_tag           (GstTagList *taglist);    /* taglist: transfer FULL */
void       gst_event_parse_tag         (GstEvent *event, GstTagList **taglist);

GstEvent * gst_event_new_gap           (GstClockTime timestamp, GstClockTime duration);
void       gst_event_parse_gap         (GstEvent *event, GstClockTime *timestamp,
                                        GstClockTime *duration);

GstEvent * gst_event_new_eos           (void);
GstEvent * gst_event_new_segment_done  (GstFormat format, gint64 position);
GstEvent * gst_event_new_reconfigure   (void);
GstEvent * gst_event_new_latency       (GstClockTime latency);
