GstQuery * gst_query_new_latency   (void);

void       gst_query_parse_latency (GstQuery     *query,
                                    gboolean     *live,
                                    GstClockTime *min_latency,
                                    GstClockTime *max_latency);

void       gst_query_set_latency   (GstQuery     *query,
                                    gboolean      live,
                                    GstClockTime  min_latency,
                                    GstClockTime  max_latency);
