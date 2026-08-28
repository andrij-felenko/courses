gboolean      (*unlock)      (GstBaseSink *sink);
gboolean      (*unlock_stop) (GstBaseSink *sink);
gboolean      (*event)       (GstBaseSink *sink, GstEvent *event);
gboolean      (*query)       (GstBaseSink *sink, GstQuery *query);

GstFlowReturn gst_base_sink_wait_preroll (GstBaseSink *sink);
GstFlowReturn gst_base_sink_wait_clock   (GstBaseSink *sink, GstClockTime time,
                                          GstClockTimeDiff *jitter);
GstFlowReturn gst_base_sink_wait         (GstBaseSink *sink, GstClockTime time,
                                          GstClockTimeDiff *jitter);
